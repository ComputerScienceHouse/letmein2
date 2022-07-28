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

type KnockClientObject struct {
	Event    string
	Location string
}

func knockCreateMQTTClient(knockID string, conn *websocket.Conn, location string, timeout int) (client mqtt.Client) {
	var broker, _ = os.LookupEnv("LMI_BROKER")
	var port, _ = os.LookupEnv("LMI_BROKER_PORT")
	var portNumber, _ = strconv.Atoi(port)

	var requestMessageHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
		fmt.Printf("/knock Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())
		// The only use the server has is listening for an ack from a
		// device.
		if msg.Topic() == "letmein2/ack" && string(msg.Payload()) != "nvm" {
			// TODO (willnilges): Give location of acknowledging device.
			message, _ := json.Marshal(KnockObject{"ACKNOWLEDGE", 0, timeout})
			conn.WriteMessage(websocket.TextMessage, message)
			conn.Close()
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

	message, _ := json.Marshal(KnockClientObject{"LOCATION", location_map[location]})
	err = conn.WriteMessage(websocket.TextMessage, message)
	if err != nil {
		log.Println("knockHandler:", err)
		return
	}

	mqttClient := knockCreateMQTTClient(knockID, conn, location, timeout)

	// Send the request to subscribed devices.
	token := mqttClient.Publish("letmein2/req", 0, false, location)
	token.Wait()

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
		err := wsConn.WriteMessage(websocket.TextMessage, message) // json go brrr
		if err != nil {
			log.Println("knockDoCountdown: ", err, ". exiting for ", knockID)
			return
		}
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
		log.Println("knockWatchForNvm:", err, ". exiting for ", knockID)
		return
	}
	clientMessageObject := KnockClientObject{}
	err = json.Unmarshal([]byte(message), &clientMessageObject)
	if err != nil {
		log.Println("knockWatchForNvm:", err, ".")
		return
	}
	if clientMessageObject.Event == "NEVERMIND" {
		fmt.Println("Got NEVERMIND at ", clientMessageObject.Location)
		wsConn.Close()
		// TODO: support this on the device lol
		token := mqttClient.Publish("letmein2/nvm", 0, false, clientMessageObject.Location)
		token.Wait()
	}
}

func knockCleanup(knockID string, wsConn *websocket.Conn, mqttClient mqtt.Client) {
	wsConn.Close()
	mqttClient.Unsubscribe("letmein2/ack")
	mqttClient.Disconnect(250)
	fmt.Println("Cleaning up knock ", knockID)
}
