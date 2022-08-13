package main

import (
    "log"
    "github.com/slack-go/slack"
)

type SlackBotInterface interface {
    testMessage()
    sendKnock()
    connectAPI()
} 

type SlackBot struct {
    api *slack.Client
    channelID string
}

func NewSlackBot(oauthToken string, channelID string) (*slack.Client) {
    return SlackBot{slack.New(oauthToken), channelID}
}

func (bot SlackBot) connectAPI(oauthToken string, channelID string) {
    bot.api = slack.New(oauthToken)
    bot.channelID = channelID
}

func (bot SlackBot) testMessage() {
    channelID, timestamp, err :=  bot.api.PostMessage(
        bot.channelID,
        slack.MsgOptionText("Test message from letmein2", false),
        slack.MsgOptionAsUser(true),
    )

    if err != nil {
        log.Fatalf("%s\n", err)
    }

    log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp);
}

func (bot SlackBot) sendKnock(username string, location string) {
    attachment := slack.Attachment {
        Pretext: "my sick-ass pretext",
        Text: "Chom from LetMeIn2",
    }

    channelID, timestamp, err := bot.api.PostMessage(
        bot.channelID,
        slack.MsgOptionText("My dope-ass primary message", false),
        slack.MsgOptionAttachments(attachment),
        slack.MsgOptionAsUser(true),
    )

    if err != nil {
        log.Fatalf("%s\n", err)
    }

    log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp);
}
