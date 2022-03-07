package main

import (
	"fmt"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gin-gonic/gin"
	"time"
)

// Slice used to keep track of active letmein requests
var req_channels []chan bool

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
	}
}

var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
	fmt.Println("Connected\n")
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
	var broker = "mqtt.csh.rit.edu"
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
	r.LoadHTMLGlob("/templates/*")
	r.Static("/static", "/static")

	// Route definitions
	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "home.tmpl", gin.H{})
	})

	r.GET("/req_s_stairs", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "s_stairs")
		token.Wait()
		c.HTML(200, "request.tmpl", gin.H{
			"location": "South Side Stairwell",
		})
	})

	r.GET("/req_n_stairs", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "n_stairs")
		token.Wait()
		c.HTML(200, "request.tmpl", gin.H{
			"location": "North Side Stairwell",
		})
	})

	r.GET("/req_level_a", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "level_a")
		token.Wait()
		c.HTML(200, "request.tmpl", gin.H{
			"location": "Level A Elevator Lobby",
		})
	})

	r.GET("/req_level_1", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "level_1")
		token.Wait()
		c.HTML(200, "request.tmpl", gin.H{
			"location": "Level 1 Elevator Lobby",
		})
	})

	r.GET("/req_l_well", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "l_well")
		token.Wait()
		c.HTML(200, "request.tmpl", gin.H{
			"location": "L Well",
		})
	})

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
	*/
	r.POST("/anybody_home", func(c *gin.Context) {
		ch := make(chan bool)
		channel_index := len(req_channels) // index of next channel added will be the old length
		request_timeout_period := 30       // TODO: Use an environment variable, you dingus!
		req_channels = append(req_channels, ch)
		select {
		case acked := <-ch:
			if acked {
				c.String(200, "acked")
			} else {
				c.String(401, "fuckoff") // it would be funny to handle different messages
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
