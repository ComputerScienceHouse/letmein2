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
    bot = SlackBot{slack.New("xoxb-4005337241633-3989795317301-PMV4AahMrWixkELYTK0CpOux"), "C03V952ENP6"}
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

    text := fmt.Sprintf("<!here> *%s* is requesting entry at *%s*", username, location)

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

func (bot SlackBot) updateStatus(knockEvent KnockEvent) {
    // Allows messages to be updated with the status of the request

    text := ""
    if knockEvent.Event == "ACKNOWLEDGE" {
        text = "This request was answered 🟢!"
    } else if knockEvent.Event == "NEVERMIND" {
        text = "This request was cancelled 🟡!"
    } else if knockEvent.Event == "TIMEOUT" {
        text = "This request timed out 🔴!"
    }

    _, channelID, timestamp, err := bot.api.UpdateMessage(
        bot.channelID,
        knockEvent.SlackMessageTS,
        slack.MsgOptionText(text, false),
        slack.MsgOptionAttachments(slack.Attachment{}),
    )

    if err != nil {
        log.Fatalf("Error: %s\n", err)
    }

    log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp)

}
