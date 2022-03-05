package main

import (
	"fmt"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	//"time"
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

func sub(client mqtt.Client) {
	topic := "letmein2/answer_usercenter"
	token := client.Subscribe(topic, 1, messagePubHandler)
	token.Wait()
	fmt.Printf("Subscribed to topic %s", topic)
}

func main() {
	var broker = "mqtt.csh.rit.edu"
	var port = 1883
	opts := mqtt.NewClientOptions()
	opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, port))
	opts.SetClientID("go_mqtt_client")
	//    opts.SetUsername("emqx")
	//    opts.SetPassword("public")
	opts.SetDefaultPublishHandler(messagePubHandler)
	opts.OnConnect = connectHandler
	opts.OnConnectionLost = connectLostHandler
	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}
	sub(client)

    r := gin.Default()
    r.SetTrustedProxies([]string{"0.0.0.0"})
    r.GET("/", func(c *gin.Context) {
        c.String(200, "Welcome to Go and Gin!")
    })
    r.GET("/req_level_a", func(c *gin.Context) {
        c.String(200, "Requesting...")
        token := client.Publish("letmein2/req_level_a", 0, false, "Hello World")
        token.Wait()
        c.String(200, "Let me in on A Level!")
    })
    r.Run()

    client.Disconnect(250)
}
