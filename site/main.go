package main

import (
    "context"
	"fmt"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gin-gonic/gin"

    recaptcha "cloud.google.com/go/recaptchaenterprise/apiv1"
    recaptchapb "google.golang.org/genproto/googleapis/cloud/recaptchaenterprise/v1"
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

/**
* Create an assessment to analyze the risk of an UI action.
*
* @param projectID: GCloud Project ID
* @param recaptchaSiteKey: Site key obtained by registering a domain/app to use recaptcha services.
* @param token: The token obtained from the client on passing the recaptchaSiteKey.
* @param recaptchaAction: Action name corresponding to the token.
*/
func createAssessment(projectID string, recaptchaSiteKey string, actionToken string, recaptchaAction string) bool {

	// Create the recaptcha client.
	// TODO: To avoid memory issues, move this client generation outside
	// of this example, and cache it (recommended) or call client.close()
	// before exiting this method.
	ctx := context.Background()
	client, err := recaptcha.NewClient(ctx)
	if err != nil {
		fmt.Printf("Error creating reCAPTCHA client:%s\n", err)
		return false
	}
	defer client.Close()

	// Set the properties of the event to be tracked.
	event := &recaptchapb.Event{
		Token:          actionToken,
		SiteKey:        recaptchaSiteKey,
	}

	assessment := &recaptchapb.Assessment{
		Event: event,
	}

	// Build the assessment request.
	request := &recaptchapb.CreateAssessmentRequest{
		Assessment: assessment,
		Parent:     fmt.Sprintf("projects/%s", projectID),
	}

	response, err := client.CreateAssessment(
		ctx,
		request)

	if err != nil {
		fmt.Printf("%v", err.Error())
		return false
	}
	// Check if the token is valid.
	if !response.TokenProperties.Valid {
		fmt.Printf("The CreateAssessment() call failed because the token"+
			" was invalid for the following reasons: %v",
		response.TokenProperties.InvalidReason)
		return false
	}

	// Check if the expected action was executed.
	if response.TokenProperties.Action == recaptchaAction {
		return response.RiskAnalysis.Score >= 0.5
	}

	fmt.Printf("The action attribute in your reCAPTCHA tag does " +
		"not match the action you are expecting to score")
	return false
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

    projectID := "coral-antonym-327500"
    recaptchaSiteKey := "6LfWXtoeAAAAAB36u5SToB1YuhCHm6mJYxUUI4Bj"
    recaptchaAction := "auth"

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

    // Homepage
	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "home.tmpl", gin.H{
            "location_map" : location_map,
        })
	})

    // Request to publish to MQTT
	r.POST("/request", func(c *gin.Context) {
        recaptcha := string(c.PostForm("recaptcha"));
		if !createAssessment(projectID, recaptchaSiteKey, recaptcha, recaptchaAction) {
			c.String(401, "Invalid Recaptcha");
			return
		}
		
		location := string(c.PostForm("location"))
        _, exists := location_map[location]
        if exists {
            token := client.Publish("letmein2/req", 0, false, location)
	    	token.Wait()
			c.HTML(200, "request.tmpl", gin.H{
                "location": location_map[location],
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
		ch := make(chan bool)
		channel_index := len(req_channels) // index of next channel added will be the old length
		request_timeout_period := 30       // TODO: Use an environment variable, you dingus!
		req_channels = append(req_channels, ch)
		select {
		case acked := <-ch:
			if acked {
				c.String(200, "acked")
			} else {
				c.String(401, "wtf") // This shouldn't happen lol
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
