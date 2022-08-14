package main

import (
    "fmt"
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

func NewSlackBot(oauthToken string, channelID string) (SlackBot) {
    return SlackBot{slack.New(oauthToken), channelID}
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
    // TODO: Allow people to answer from Slack?
    /*attachment := slack.Attachment {
        Pretext: "my sick-ass pretext",
        Text: "Chom from LetMeIn2",
    }*/

    // TODO: Change the channel back to bot.channelID
    request := fmt.Sprintf("*%s* is requesting entry at *%s*", username, location);
    channelID, timestamp, err := bot.api.PostMessage(
        bot.channelID,
        slack.MsgOptionText(request, false),
        slack.MsgOptionAsUser(true),
    )

    if err != nil {
        log.Fatalf("%s\n", err)
    }

    log.Printf("Request sent to Channel %s at %s\n", channelID, timestamp);
}
