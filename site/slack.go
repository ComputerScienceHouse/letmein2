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
	api        *slack.Client
	channelID  string
	isValidBot bool
}

func NewSlackBot(oauthToken string, channelID string) SlackBot {
	var isValid bool = true
	if oauthToken == "" || channelID == "" {
		isValid = false
		fmt.Println("== The SlackBot is not valid, any requests will be Ignored! ==")
	}
	bot = SlackBot{slack.New(oauthToken), channelID, isValid}
	return bot
}

func (bot SlackBot) testMessage() {
	if !bot.isValidBot {
		return
	}
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
	if !bot.isValidBot {
		return
	}

	text := fmt.Sprintf("@here *%s* is requesting entry at *%s*", username, location)

	attachment := slack.Attachment{
		Pretext:    "",
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
		slack.MsgOptionText(text, false),
		slack.MsgOptionAttachments(attachment),
	)

	if err != nil {
		log.Fatalf("Error: %s\n", err)
	}

	log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)
	return timestamp

}

func (bot SlackBot) updateStatus(knockEvent KnockEvent, username string, location string) {
	// Allows messages to be updated with the status of the request
	if !bot.isValidBot {
		return
	}

	text := ""
	if knockEvent.Event == "ACKNOWLEDGE" {
		text = fmt.Sprintf("This request was answered 🟢!\nUser: %s\nLocation: %s", username, location)
	} else if knockEvent.Event == "NEVERMIND" {
		text = fmt.Sprintf("This request was cancelled 🟡!\nUser: %s\nLocation: %s", username, location)
	} else if knockEvent.Event == "TIMEOUT" {
		text = fmt.Sprintf("This request timed out 🔴!\nUser: %s\nLocation: %s", username, location)
	}

	_, channelID, timestamp, err := bot.api.UpdateMessage(
		bot.channelID,
		knockEvent.SlackMessageTS,
		slack.MsgOptionText(text, false),
		// blank attachment here to clear any previous attachments
		slack.MsgOptionAttachments(slack.Attachment{}),
	)

	if err != nil {
		log.Fatalf("Error: %s\n", err)
	}

	log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)
}
