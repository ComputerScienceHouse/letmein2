package main

import (
	"fmt"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"time"
    "os"
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
	token := client.Subscribe(topic, 1, nil)
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
    /*
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}*/

    if token := client.Subscribe("letmein2/answer_usercenter", 0, nil); token.Wait() && token.Error() != nil {
            fmt.Println("dingus");
            fmt.Println(token.Error())
            os.Exit(1)
    }

    for {
            time.Sleep(1 * time.Second)
            //fmt.Println("waiting: ", wcount)
            //wcount += 1
    }
    client.Disconnect(250)
}
