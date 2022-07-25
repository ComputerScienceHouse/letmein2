package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var mqtt_id int = 0

// Iotas to represent the state of any possible location
// const (
// 	IDLE int = iota
// 	WAITING
// 	ANSWERED
// 	TIMEOUT
// )

// Set up locations (TODO: Config file?)
// var location_status sync.Map

// Location map should map the later sync.Map 1:1
var location_map = map[string]string{
	"n_stairs": "North Side Stairwell",
	"s_stairs": "South Side Stairwell",
	"level_a":  "Level A Elevator Lobby",
	"level_1":  "Level 1 Elevator Lobby",
	"l_well":   "L Well",
}

// TODO: Structured logging into Datadog?

func mqttSubTopic(client mqtt.Client, handler mqtt.MessageHandler, topic string) {
	token := client.Subscribe(topic, 1, handler)
	token.Wait()
	fmt.Printf("Subscribed to topic %s\n", topic)
}

var wsUpgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

type KnockObject struct {
	Event       string
	CurrentTime int
	MaxTime     int
}

func knockCreateMQTTClient(knockID string, conn *websocket.Conn, location string, timeout int) (client mqtt.Client) {
	var broker, _ = os.LookupEnv("LMI_BROKER")
	var port, _ = os.LookupEnv("LMI_BROKER_PORT")
	var portNumber, _ = strconv.Atoi(port)

	var requestMessageHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
		fmt.Printf("/knock Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())
		if msg.Topic() == "letmein2/ack" {
			// TODO (willnilges): Give location of acknowledging device.
			message, _ := json.Marshal(KnockObject{"ACKNOWLEDGE", 0, timeout})
			conn.WriteMessage(websocket.TextMessage, message)
		}
	}

	cliOp := mqtt.NewClientOptions()
	cliOp.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, portNumber))
	cliOp.SetClientID(knockID)
	cliOp.SetDefaultPublishHandler(requestMessageHandler)

	client = mqtt.NewClient(cliOp)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}

	mqttSubTopic(client, requestMessageHandler, "letmein2/ack")
	return
}

func knockHandler(c *gin.Context) {
	location := c.Param("location")
	knockID := location + fmt.Sprintf("%d", mqtt_id)
	mqtt_id++
	w := c.Writer
	r := c.Request

	timeoutEnv, _ := os.LookupEnv("LMI_TIMEOUT")
	timeout, _ := strconv.Atoi(timeoutEnv)

	fmt.Println("Somebody has knocked. Timeout is ", timeout, "s")

	// Set up a websocket connection with the client.
	conn, err := wsUpgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Println("Failed to set websocket upgrade: %+v", err)
		c.String(500, "Failed to set websocket upgrade.")
		return
	}

	mqttClient := knockCreateMQTTClient(knockID, conn, location, timeout)

	// 1 second offset to make the timeout modal look better.
	go knockDoCountdown(knockID, conn, mqttClient, timeout+1)

	// Separate goroutine to handle reading websocket data
	go knockReadClientMsg(knockID, conn, mqttClient)

	// Set read deadline. This will kill the websocket and related functions
	// if the request times out.
	conn.SetReadDeadline(time.Now().Add(time.Duration(timeout+2) * time.Second))
}

func knockDoCountdown(knockID string, wsConn *websocket.Conn, mqttClient mqtt.Client, timeout int) {
	defer knockCleanup(knockID, wsConn, mqttClient)
	for i := timeout; i > 0; i-- {
		message, _ := json.Marshal(KnockObject{"COUNTDOWN", i, timeout})
		wsConn.WriteMessage(websocket.TextMessage, message) // json go brrr
		time.Sleep(1 * time.Second)
	}
	token := mqttClient.Publish("letmein2/ack", 0, false, "timeout")
	token.Wait()
	timeoutMessage, _ := json.Marshal(KnockObject{"TIMEOUT", 0, timeout})
	wsConn.WriteMessage(websocket.TextMessage, timeoutMessage)
}

func knockReadClientMsg(knockID string, wsConn *websocket.Conn, mqttClient mqtt.Client) {
	// defer knockCleanup(knockID, wsConn, mqttClient)
	_, message, err := wsConn.ReadMessage()
	if err != nil {
		log.Println("knockWatchForNvm:", err)
		return
	}
	if string(message) == "NEVERMIND" {
		fmt.Println("Got NEVERMIND!")
		token := mqttClient.Publish("letmein2/ack", 0, false, "nvm")
		token.Wait()
	}
}

func knockCleanup(knockID string, wsConn *websocket.Conn, mqttClient mqtt.Client) {
	wsConn.Close()
	mqttClient.Unsubscribe("letmein2/ack")
	mqttClient.Disconnect(250)
	fmt.Println("Cleaning up knock ", knockID)
}

func main() {
	// Get environment variables
	var broker, brokerMissing = os.LookupEnv("LMI_BROKER")
	var port, portMissing = os.LookupEnv("LMI_BROKER_PORT")
	var portNumber = 1883 // Set a reasonable default.
	var lmiTemplates, lmiTemplatesMissing = os.LookupEnv("LMI_TEMPLATES")
	var lmiStatic, lmiStaticMissing = os.LookupEnv("LMI_STATIC")

	var timeout, timeoutMissing = os.LookupEnv("LMI_TIMEOUT")
	var timeoutPeriod = 45 // Set a reasonable default.

	// Make sure the variables actually exist
	if !brokerMissing {
		fmt.Println("Error! MQTT Broker not specified.")
		return
	}

	if !portMissing {
		fmt.Println("Warning! MQTT Port not specified. Defaulting to 1883...")
	} else {
		portNumber, _ = strconv.Atoi(port)
	}

	if !lmiTemplatesMissing {
		fmt.Println("Error! LMI_TEMPLATES not specified.")
		return
	}

	if !lmiStaticMissing {
		fmt.Println("Error! LMI_STATIC not specified.")
		return
	}

	if !timeoutMissing {
		fmt.Println("Warning! Timeout not specified. Defaulting to ", timeoutPeriod, "...")
	} else {
		timeoutPeriod, _ = strconv.Atoi(timeout)
	}

	/*
		TODO: This idiot will change any idiot from the "waiting" state to the "ack'ed" state.
		It will not handle "timeout," because that's fucking stupid :)

		TODO: Still need to implement states and check out what happens when you have multiple
		requests on one door and on multiple doors and shit like that.
	*/

	// Handle messages from subscribed topics
	var messagePubHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
		fmt.Printf("Main Server Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())
	}

	var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
		fmt.Println("Connected to MQTT server")
	}

	var connectLostHandler mqtt.ConnectionLostHandler = func(client mqtt.Client, err error) {
		fmt.Printf("Connect lost: %v\n", err)
	}

	fmt.Println("Configuring Server's MQTT Client. MQTT broker = ", broker, ", port = ", portNumber)
	opts := mqtt.NewClientOptions()
	opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, portNumber))
	opts.SetClientID("main_server")
	opts.SetDefaultPublishHandler(messagePubHandler)
	opts.OnConnect = connectHandler
	opts.OnConnectionLost = connectLostHandler
	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}

	// Subscribe to topics
	// sub(client, "letmein2/req") // I don't think the server needs to subscribe to requests...?
	// sub(client, "letmein2/ack")

	// Gin Setup
	r := gin.Default()
	r.SetTrustedProxies([]string{"0.0.0.0"})

	r.LoadHTMLGlob(lmiTemplates)
	r.Static("/static", lmiStatic)

	// ===== Route definitions =====

	// Homepage
	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "home.tmpl", gin.H{
			"location_map": location_map,
		})
	})

	/* Returns the current timeout period of the server. Could be used to get...
	whatever else in the future. */
	r.GET("/session_info", func(c *gin.Context) {
		c.String(200, strconv.Itoa(timeoutPeriod))
	})

	/* Route for requesting entry. Fires off an MQTT request. If it
	works, returns 200, so that the client can send an 'anybody_home' */
	r.POST("/request/:location", func(c *gin.Context) {
		userRequest := c.Param("location")
		_, exists := location_map[userRequest]
		if exists {
			token := client.Publish("letmein2/req", 0, false, userRequest)
			token.Wait()
			c.String(200, location_map[userRequest])
		} else {
			c.String(404, "Unknown Location.")
		}
	})

	// For canceling requests
	r.POST("/nvm", func(c *gin.Context) {
		token := client.Publish("letmein2/ack", 0, false, "nvm")
		token.Wait()
		c.Redirect(302, "/")
	})

	r.GET("/knock/socket/:location", knockHandler)

	/*
		POST request sent by clients when they select a location.
		Will set up a channel, then wait a given amount of time for
		an answer. If an answer is received, it will resolve to a 200,
		otherwise it'll 403.

		This is kinda cringe. Less cringe. But still cringe.
	*/

	// Once the request is successfully sent, the client should call this,
	// and wait for a box to respond.
	r.POST("/anybody_home/:location", func(c *gin.Context) {
		userRequest := c.Param("location")
		var broker, _ = os.LookupEnv("LMI_BROKER")
		var port, _ = os.LookupEnv("LMI_BROKER_PORT")
		var portNumber, _ = strconv.Atoi(port)

		requestChannel := make(chan string)

		var requestMessageHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
			fmt.Printf("/anybody_home Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())
			if msg.Topic() == "letmein2/ack" {
				requestChannel <- string(msg.Payload())
			}
		}

		fmt.Println("Creating /anybody_home ", userRequest, " MQTT broker ", broker, " port ", portNumber)
		reqOp := mqtt.NewClientOptions()
		reqOp.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, portNumber))
		reqOp.SetClientID(userRequest + fmt.Sprintf("%d", mqtt_id))
		mqtt_id++
		reqOp.SetDefaultPublishHandler(requestMessageHandler)
		reqOp.OnConnect = connectHandler
		reqOp.OnConnectionLost = connectLostHandler
		reqCli := mqtt.NewClient(reqOp)
		if token := reqCli.Connect(); token.Wait() && token.Error() != nil {
			panic(token.Error())
		}
		mqttSubTopic(reqCli, requestMessageHandler, "letmein2/ack")
		select {
		case acked := <-requestChannel:
			if acked == "nvm" {
				c.String(302, "/")
			} else if acked == "timeout" {
				c.String(403, acked) // This feels dumb...
			} else {
				fmt.Println("Got an answer! Returning 200!")
				c.String(200, "acked")
			}
		case <-time.After(time.Second * time.Duration(timeoutPeriod)):
			fmt.Println("Request timed out. Returning 403!")
			c.String(403, "timeout")
			token := reqCli.Publish("letmein2/ack", 0, false, "timeout")
			token.Wait()
		}
		close(requestChannel)
		reqCli.Unsubscribe("letmein2/ack")
		reqCli.Disconnect(250)
		fmt.Println("Bye bye!")
	})

	r.Run()
	client.Disconnect(250)
}
