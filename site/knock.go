package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

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

// TODO (willnilges): Structured logging into Datadog

var wsUpgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

type KnockInterface interface {
    handler()
    createMQTTClient()
}

type Knock struct {
    slackBot SlackBot
    mqttID int
    broker string
    port int
    timeout int
}

// Functions to handle requests from the webserver
func (knock *Knock) handler(c *gin.Context) {
	location := c.Param("location")
	knockID := location + fmt.Sprintf("_%d", knock.mqttID)
	knock.mqttID++
	w := c.Writer
	r := c.Request

	fmt.Println("Somebody has knocked. ID is ", knockID ," Timeout is ", knock.timeout, "s")

	// Set up a websocket connection with the client.
	conn, err := wsUpgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Println("Failed to set websocket upgrade: %+v", err)
		c.String(500, "Failed to set websocket upgrade.")
		return
	}

    // Create a new event to keep track of everything
    knockEvent := KnockEvent {
        ID: knockID,
        Event: "LOCATION",
        CurrentTime: 0,
        MaxTime: knock.timeout,
        Name: "",
        Location: location_map[location],
        ShortLocation: location,
    }

	message, _ := json.Marshal(knockEvent)
	err = conn.WriteMessage(websocket.TextMessage, message)
	if err != nil {
		log.Println("knockHandler:", err)
		return
	}

	mqttClient := knock.createMQTTClient(conn, knockEvent)

	// Send the request to subscribed devices.
	token := mqttClient.Publish("letmein2/req", 0, false, location)
	token.Wait()

	// 1 second offset to make the timeout modal look better.
	go knockEvent.doCountdown(conn, mqttClient, knock.timeout+1)

	// Separate goroutine to handle reading websocket data
	go knockEvent.readClientMsg(conn, mqttClient, knock.slackBot)

	// Set read deadline. This will kill the websocket and related functions
	// if the request times out.
	conn.SetReadDeadline(time.Now().Add(time.Duration(knock.timeout+2) * time.Second))
}

func (knock Knock) createMQTTClient(conn *websocket.Conn, knockEvent KnockEvent) (client mqtt.Client) {
	var requestMessageHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
		fmt.Printf("/knock Received message \"%s\" from topic \"%s\"\n", msg.Payload(), msg.Topic())
		// The only use the server has is listening for an ack from a
		// device.
		if msg.Topic() == "letmein2/ack" && string(msg.Payload()) != "nvm" && string(msg.Payload()) != "timeout" {
			// TODO (willnilges): Give location of acknowledging device.
            knockEvent.Event = "ACKNOWLEDGE"
            knockEvent.CurrentTime = 0;
			message, _ := json.Marshal(knockEvent)
			conn.WriteMessage(websocket.TextMessage, message)
			conn.Close()
		}
	}

	cliOp := mqtt.NewClientOptions()
	cliOp.AddBroker(fmt.Sprintf("tcp://%s:%d", knock.broker, knock.port))
	cliOp.SetClientID(knockEvent.ID)
	cliOp.SetDefaultPublishHandler(requestMessageHandler)

	client = mqtt.NewClient(cliOp)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}

	mqttSubTopic(client, requestMessageHandler, "letmein2/ack")
	return
}

func mqttSubTopic(client mqtt.Client, handler mqtt.MessageHandler, topic string) {
	token := client.Subscribe(topic, 1, handler)
	token.Wait()
	fmt.Printf("Subscribed to topic %s\n", topic)
}


type KnockEventInterface interface {
    doCountdown()
    readClientMsg()
    cleanup()
}

type KnockEvent struct {
    ID            string
    Event         string
    CurrentTime   int
    MaxTime       int
    Name          string
    Location      string
    ShortLocation string
}

func (knockEvent KnockEvent) doCountdown(wsConn *websocket.Conn, mqttClient mqtt.Client, timeout int) {
	defer knockEvent.cleanup(wsConn, mqttClient)
	for i := knockEvent.MaxTime; i > 0; i-- {
        knockEvent.Event = "COUNTDOWN"
        knockEvent.CurrentTime = i;
		message, _ := json.Marshal(knockEvent)
		err := wsConn.WriteMessage(websocket.TextMessage, message) // json go brrr
		if err != nil {
			log.Println("knockDoCountdown: ", err, ". exiting for ", knockEvent.ID)
			return
		}
		time.Sleep(1 * time.Second)
	}
	token := mqttClient.Publish("letmein2/timeout", 0, false, knockEvent.ShortLocation)
	token.Wait()
    knockEvent.Event = "TIMEOUT"
    knockEvent.CurrentTime = 0;
	timeoutMessage, _ := json.Marshal(knockEvent)
	wsConn.WriteMessage(websocket.TextMessage, timeoutMessage)
}

func (knockEvent KnockEvent) readClientMsg(wsConn *websocket.Conn, mqttClient mqtt.Client, bot SlackBot) {
    for {
        _, message, err := wsConn.ReadMessage()
        if err != nil {
            log.Println("knockWatchForNvm:", err, ". exiting for ", knockEvent.ID)
            return
        }
        clientMessageObject := KnockEvent{}
        err = json.Unmarshal([]byte(message), &clientMessageObject)
        fmt.Println("Recieved message from client in session ", knockEvent.ID, ". Message: ", clientMessageObject);
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
        if clientMessageObject.Event == "NAME" {
            fmt.Println("Got NAME: ", clientMessageObject.Name)
            go bot.sendKnock(clientMessageObject.Name, location_map[clientMessageObject.Location])
        }
    }
}

func (knockEvent KnockEvent) cleanup(wsConn *websocket.Conn, mqttClient mqtt.Client) {
	wsConn.Close()
	mqttClient.Unsubscribe("letmein2/ack")
	mqttClient.Disconnect(250)
	fmt.Println("Cleaning up knock ", knockEvent.ID)
}
