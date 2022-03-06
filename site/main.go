package main

import (
	"fmt"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"time"
	"github.com/gin-gonic/gin"
)

var messagePubHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
	fmt.Printf("Received message: %s from topic: %s\n", msg.Payload(), msg.Topic())
    
}

var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
	fmt.Println("Connected")
}

var connectLostHandler mqtt.ConnectionLostHandler = func(client mqtt.Client, err error) {
	fmt.Printf("Connect lost: %v", err)
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
	sub(client, "letmein2/req")
	sub(client, "letmein2/ack")

    // Gin Setup
	r := gin.Default()
	r.SetTrustedProxies([]string{"0.0.0.0"})
	r.LoadHTMLGlob("/templates/*")
	r.Static("/static", "/static")

    // Route definitions
	r.GET("/", func(c *gin.Context) {
		//c.String(200, "Welcome to LetMeIn2!")
        c.HTML(200, "home.tmpl", gin.H{})

	})

	r.GET("/req_s_stairs", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "s_stairs")
		token.Wait()
        //c.String(200, "Let me in on S Stairs!")
        c.HTML(200, "request.tmpl", gin.H{
		"location": "South Side Stairwell",
        })
	})

	r.GET("/req_n_stairs", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "n_stairs")
		token.Wait()
		c.String(200, "Let me in on N Stairs!")
	})

	r.GET("/req_level_a", func(c *gin.Context) {
		token := client.Publish("letmein2/req", 0, false, "level_a")
		token.Wait()
		c.String(200, "Let me in on Level A!")
	})

	r.GET("/req_level_1", func(c *gin.Context) {
		token := client.Publish("letmein3/req", 0, false, "level_1")
		token.Wait()
		c.String(200, "Let me in on Level 1!")
	})

    r.POST("/response_acked", func(c *gin.Context) {
        time.Sleep(3000 * time.Millisecond)
        c.String(200, "timeout");
    })

	r.Run()

	client.Disconnect(250)
}
