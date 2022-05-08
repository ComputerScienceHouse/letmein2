package main

import (
	"os"
	"fmt"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gin-gonic/gin"
)

// Slice of channels used to keep track of active letmein requests
var req_channels []chan bool

var location_map = map[string]string{
	"n_stairs": "North Side Stairwell",
	"s_stairs": "South Side Stairwell",
	"level_a":  "Level A Elevator Lobby",
	"level_1":  "Level 1 Elevator Lobby",
	"l_well":   "L Well",
}

// TODO: Structured logging into Datadog?
// Handle messages from subscribed topics
var messagePubHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
	fmt.Printf("Received message: %s from topic: %s\n", msg.Payload(), msg.Topic())

	/*
	   If we receive an ack message that isn't a timeout, then set each active
	   channel to 'true' (that'll cause the webpage the client is looking at to
	   update and notify them of the good news), and then set the req_channels
	   slice to nil to kill any references to the channels we're about to close.
	*/
	if msg.Topic() == "letmein2/ack" && string(msg.Payload()) != "timeout" {
		for _, c := range req_channels {
			if c != nil {
				c <- true
			}
		}
		req_channels = nil
	} else if msg.Topic() == "letmein2/ack" && string(msg.Payload()) == "timeout" { // uhh cheeseburger
		for _, c := range req_channels {
			if c != nil {
				c <- false
			}
		}
		req_channels = nil
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
	fmt.Printf("Subscribed to topic %s", topic)
}

func main() {
	// MQTT setup (and a lot of it)
	var broker = os.Getenv("LMI_BROKER")
	var port = 1883
	opts := mqtt.NewClientOptions()
	opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, port))
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
	sub(client, "letmein2/ack")

	// Gin Setup
	r := gin.Default()
	r.SetTrustedProxies([]string{"0.0.0.0"})
	fmt.Println(os.Getenv("LMI_TEMPLATES"))
	fmt.Println(os.Getenv("LMI_STATIC"))

	r.LoadHTMLGlob(os.Getenv("LMI_TEMPLATES"))
	r.Static(os.Getenv("LMI_STATIC"), "/static")

	// r.LoadHTMLGlob("/home/wilnil/Code/letmein2/site/templates/*")
	// r.Static("/home/wilnil/Code/letmein2/site/static", "/static")

	// r.LoadHTMLGlob("/templates/*")
	// r.Static("/static", "/static")

	// Route definitions

    // Homepage
	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "home.tmpl", gin.H{
            "location_map" : location_map,
        })
	})

    // Request to publish to MQTT
	r.POST("/request/:location", func(c *gin.Context) {
        _, exists := location_map[c.Param("location")]
        if exists {
            token := client.Publish("letmein2/req", 0, false, c.Param("location"))
	    	token.Wait()
        } else {
            c.String(404, "Unknown Location.");
        }
	})
    
    // Request to load the waiting screen 
    r.GET("/request/:location", func(c *gin.Context) {
        _, exists := location_map[c.Param("location")]
        if exists {
            c.HTML(200, "request.tmpl", gin.H{
                "location": location_map[c.Param("location")],
            })
        } else {
            c.String(404, "Unknown Location.");
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
	r.POST("/anybody_home", func(c *gin.Context) {
		request_timeout_period := 10       // TODO: Use an environment variable, you dingus!

		ch := make(chan bool)
		channel_index := len(req_channels) // index of next channel added will be the old length
		req_channels = append(req_channels, ch)
		select {
		case acked := <-ch:
			if acked {
				c.String(200, "acked")
			} else {
				//c.String(401, "wtf") // This shouldn't happen lol
				c.String(408, "timeout")
			}
		case <-time.After(time.Second * time.Duration(request_timeout_period)):
			// Remove a timed out channel from the channel slice, as to not crash the server :)
			req_channels[channel_index] = req_channels[len(req_channels)-1]
			req_channels = req_channels[:len(req_channels)-1]

			c.String(408, "timeout")
			token := client.Publish("letmein2/ack", 0, false, "timeout")
			token.Wait()
		}
		close(ch)
	})

	r.Run()

	// chom
	client.Disconnect(250)
}
