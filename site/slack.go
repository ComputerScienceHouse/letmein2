package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/slack-go/slack"
)

var bot SlackBot
var httpRegistered bool = false

type SlackBotInterface interface {
	testMessage()
	sendKnock()
	connectAPI()
}

type SlackBot struct {
	api       *slack.Client
	channelID string
}

func NewSlackBot(oauthToken string, channelID string) SlackBot {
	//registerHTTP()
	bot = SlackBot{slack.New("xoxb-4005337241633-3989795317301-RRI8WsutUxJ0PysCiYCjkQG9"), "C03V952ENP6"}
	return bot
}

func (bot SlackBot) testMessage() {
	channelID, timestamp, err := bot.api.PostMessage(
		bot.channelID,
		slack.MsgOptionText("Test message from letmein2", false),
		slack.MsgOptionAsUser(true),
	)

	if err != nil {
		log.Fatalf("%s\n", err)
	}

	log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)
}

func (bot SlackBot) sendKnock(username string, location string) {
	// TODO: Allow people to answer from Slack?
	/*attachment := slack.Attachment {
	    Pretext: "my sick-ass pretext",
	    Text: "Chom from LetMeIn2",
	}*/

	pretext := fmt.Sprintf("<!here> *%s* is requesting entry at *%s*", username, location)

	attachment := slack.Attachment{
		Pretext:    pretext,
		Fallback:   "Your Slack client is not supported",
		CallbackID: "letmein_accept",
		Color:      "#32CD32",
		Actions: []slack.AttachmentAction{
			{
				Name:  "accept",
				Text:  "Rescue",
				Type:  "button",
				Value: "accept",
			},
		},
	}

	channelID, timestamp, err := bot.api.PostMessage(
		bot.channelID,
		slack.MsgOptionText("", false),
		slack.MsgOptionAttachments(attachment),
	)

	if err != nil {
		log.Fatalf("Error: %s\n", err)
	}

	log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)
	//registerHTTP()

}
func buttonHandler(c *gin.Context) {
	requestBody, err := io.ReadAll(c.Request.Body)
	requestBodyString := strings.TrimLeft(string(requestBody[:]), "payload=")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%22", "\"")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%7B", "{")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%3A", ":")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%2C", ",")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%5B", "[")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%7D", "}")
	requestBodyString = strings.ReplaceAll(requestBodyString, "%5D", "]")

	var payload slack.InteractionCallback
	err = json.Unmarshal([]byte(requestBodyString), &payload)

	//log.Printf("Entered button handler, %s", requestBodyString)
	if err != nil {
		log.Fatalf("Error: %s\n", err)
	}

	channelID, timestamp, err := bot.api.PostMessage(
		bot.channelID,
		slack.MsgOptionText(fmt.Sprintf("*%s* is on the rescue!", payload.User.Name), false),
		slack.MsgOptionAsUser(true),
		slack.MsgOptionTS(payload.MessageTs),
	)
	if err != nil {
		log.Fatalf("Error: %s\n", err)
	}
	log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)
}
