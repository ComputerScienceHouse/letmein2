package main

import (
	"fmt"
	"os"
	"strconv"
	"sync"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gin-gonic/gin"
)

// Slice of channels used to keep track of active letmein requests
var req_channels []chan bool

var mqtt_id int = 0

// Iotas to represent the state of any possible location
const (
	IDLE int = iota
	WAITING
	ANSWERED
	TIMEOUT
)

// Set up locations (TODO: Config file?)
var location_status sync.Map

// Location map should map the later sync.Map 1:1
var location_map = map[string]string{
	"n_stairs": "North Side Stairwell",
	"s_stairs": "South Side Stairwell",
	"level_a":  "Level A Elevator Lobby",
	"level_1":  "Level 1 Elevator Lobby",
	"l_well":   "L Well",
}

// TODO: Structured logging into Datadog?

// TODO: This idiot will change any idiot from the "waiting" state to the "ack'ed"
// state. It will not handle "timeout," because that's fucking stupid :)

// Handle messages from subscribed topics
var messagePubHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
	fmt.Printf("Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())

	/*
	   If we receive an ack message that isn't a timeout, then set each active
	   channel to 'true' (that'll cause the webpage the client is looking at to
	   update and notify them of the good news), and then set the req_channels
	   slice to nil to kill any references to the channels we're about to close.
	*/
	if msg.Topic() == "letmein2/ack" && string(msg.Payload()) != "timeout" {
		for k, _ := range location_map {
			location_status.Store(k, ANSWERED)
		}

	} else if msg.Topic() == "letmein2/ack" && string(msg.Payload()) == "nvm" {
		for k, _ := range location_map {
			location_status.Store(k, IDLE) // TODO: This is wrong. This needs to cancel just one door. I think Max's way of doing this might actually work out better.
		}
	}
}

var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
	fmt.Println("Connected to MQTT server\n")
}

var connectLostHandler mqtt.ConnectionLostHandler = func(client mqtt.Client, err error) {
	fmt.Printf("Connect lost: %v\n", err)
}

func sub(client mqtt.Client, topic string) {
	token := client.Subscribe(topic, 1, messagePubHandler)
	token.Wait()
	fmt.Println("Subscribed to topic %s", topic)
}

func mqttSubTopic(client mqtt.Client, handler mqtt.MessageHandler, topic string) {
	token := client.Subscribe(topic, 1, handler)
	token.Wait()
	fmt.Println("Subscribed to topic %s\n", topic)
}

func main() {
	for k, _ := range location_map {
		location_status.Store(k, IDLE)
	}

	// Get environment variables
	var broker, brokerMissing = os.LookupEnv("LMI_BROKER")
	var port, portMissing = os.LookupEnv("LMI_BROKER_PORT")
	var portNumber = 1883 // Set a reasonable default.
	var lmiTemplates, lmiTemplatesMissing = os.LookupEnv("LMI_TEMPLATES")
	var lmiStatic, lmiStaticMissing = os.LookupEnv("LMI_STATIC")

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

	fmt.Println("MQTT broker ", broker, " port ", portNumber)
	opts := mqtt.NewClientOptions()
	opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, portNumber))
	opts.SetClientID("go_mqtt_client")
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
		c.HTML(200, "home.html", gin.H{
			"location_map": location_map,
		})
	})

	// Request to publish to MQTT
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
	r.GET("/nvm", func(c *gin.Context) {
		token := client.Publish("letmein2/ack", 0, false, "nvm")
		token.Wait()
		c.Redirect(302, "/")
	})

	/*
			   POST request sent by clients when they select a location.
			   Will set up a channel, then wait a given amount of time for
			   an answer. If an answer is received, it will resolve to a 200,
			   otherwise it'll 408.

		       This is kinda cringe
	*/
	// r.POST("/anybody_home", func(c *gin.Context) {
	// 	request_timeout_period := 10       // TODO: Use an environment variable, you dingus!

	// 	ch := make(chan bool)
	// 	channel_index := len(req_channels) // index of next channel added will be the old length
	// 	req_channels = append(req_channels, ch)
	// 	select {
	// 	case acked := <-ch:
	// 		if acked {
	// 			c.String(200, "acked")
	// 		} else {
	// 			//c.String(401, "wtf") // This shouldn't happen lol
	// 			c.String(408, "timeout")
	// 		}
	// 		req_channels[channel_index] = req_channels[len(req_channels)-1]
	// 		req_channels = req_channels[:len(req_channels)-1]
	// 	case <-time.After(time.Second * time.Duration(request_timeout_period)):
	// 		// Remove a timed out channel from the channel slice, as to not crash the server :)
	// 		req_channels[channel_index] = req_channels[len(req_channels)-1]
	// 		req_channels = req_channels[:len(req_channels)-1]

	// 		c.String(408, "timeout")
	// 		token := client.Publish("letmein2/ack", 0, false, "timeout")
	// 		token.Wait()
	// 	}
	// 	close(ch)
	// })

	r.POST("/anybody_home/:location", func(c *gin.Context) {
		userRequest := c.Param("location")
		var broker, _ = os.LookupEnv("LMI_BROKER")
		var port, _ = os.LookupEnv("LMI_BROKER_PORT")
		var portNumber, _ = strconv.Atoi(port)

		fmt.Println("MQTT broker ", broker, " port ", portNumber)
		opts := mqtt.NewClientOptions()
		opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, portNumber))
		opts.SetClientID(userRequest + fmt.Sprintf("%d", mqtt_id))
		mqtt_id++
		opts.SetDefaultPublishHandler(messagePubHandler)
		opts.OnConnect = connectHandler
		opts.OnConnectionLost = connectLostHandler
		requestClient := mqtt.NewClient(opts)
		if token := requestClient.Connect(); token.Wait() && token.Error() != nil {
			panic(token.Error())
		}

		requestChannel := make(chan string)

		var requestMessageHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
			fmt.Printf("/anybody_home Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())
			if msg.Topic() == "letmein2/ack" && string(msg.Payload()) != "timeout" {
				requestChannel <- "ack"
			}
		}

		// Subscribe to topics
		mqttSubTopic(requestClient, requestMessageHandler, "letmein2/ack")

		request_timeout_period := 10 // TODO: Use an environment variable, you dingus!
		cooldown_period := 1
		userRequestStatus, _ := location_status.Load(userRequest)
		switch userRequestStatus {
		case IDLE:
			location_status.Store(userRequest, WAITING)
			select {
			case acked := <-requestChannel:
				if acked == "ack" {
					fmt.Printf("Returning ack....\n")
					location_status.Store(userRequest, ANSWERED)
					c.String(200, "acked")
					return
				}
			case <-time.After(time.Second * time.Duration(request_timeout_period)):
				c.String(408, "timeout")
				token := requestClient.Publish("letmein2/ack", 0, false, "timeout")
				token.Wait()
				return
			}
		case WAITING:
			// Not sure how to return the current timer. Hold on...
		case ANSWERED:
			fallthrough
		case TIMEOUT:
			select {
			case <-time.After(time.Second * time.Duration(cooldown_period)):
				location_status.Store(userRequest, IDLE)
			}
		}
	})

	r.Run()

	// chom
	client.Disconnect(250)
}
