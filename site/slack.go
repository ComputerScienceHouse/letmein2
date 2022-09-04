package main

import (
	"fmt"
	"log"

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
	bot = SlackBot{slack.New("xoxb-4005337241633-3989795317301-SSTJTiSY5xC9VMIMb3BVXNH0"), "C03V952ENP6"}
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

func (bot SlackBot) sendKnock(username string, location string) (messagets string) {
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
	return timestamp

}

func (bot SlackBot) sendReply(messagets string, subtopic string) {
	// TODO: Allow people to answer from Slack?
	/*attachment := slack.Attachment {
	    Pretext: "my sick-ass pretext",
	    Text: "Chom from LetMeIn2",
	}*/

	text := ""
	if subtopic == "ack" {
		text = "Someone is coming to get you!"
	} else if subtopic == "nvm" {
		text = "This request was cancelled!"
	} else if subtopic == "timeout" {
		text = "This request timed out!"
	}

	channelID, timestamp, err := bot.api.PostMessage(
		bot.channelID,
		slack.MsgOptionText(text, false),
		slack.MsgOptionTS(messagets),
	)

	if err != nil {
		log.Fatalf("Error: %s\n", err)
	}

	log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)

}
