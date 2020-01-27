# Mister Moji
## An LED Panel for your Slack emoji reactions.

## Initial setup

### Setting up your Raspberry Pi
TODO: Write here - how far to go? Don't want readme to be tutorial 

### Install required dependencies

```
sudo chmod +x install.sh
sudo ./install.sh
```

##  Setup and running the Slack portion

### Create a Slack App
Create a Slack app on https://api.slack.com/apps/

* Add a bot user to your app
* Install the app on your team
* Authorize the app
* Add your bot's tokens to your environmental variables (paste in terminal):
  `export SLACK_BOT_TOKEN=xxxXXxxXXxXXxXXXXxxxX.xXxxxXxxxx`
  You will need:
    * `SLACK_BOT_TOKEN`
    * `SLACK_SIGNING_SECRET`
    * `SLACK_BOT_OAUTH_TOKEN`
* Give your bot permissions (under 'Scope' in 'OAuth and Permissions'):
  * `reactions:read`
  * `users:read`
  * `users:profile:read`
  * `channels:read`

### Start ngrok
We'll use [ngrok](https://ngrok.com) so that Slack can communicate with our local server.

To start `ngrok`: `./ngrok http 3000`

Copy and paste the `https` address for your local server, then go to your Slack app and click on 'Event Subscriptions'. Enable events and paste your `ngrok` `https` address to the 'Request URL'. *Save your changes*

### Run the app
Make sure the `ngrok` server is running and type:

`python slackbot.py`

### Get your user ID.
Follow the instructions in `slackbot.py` to find your user ID and add that value to the `userID` variable. Restart the app.

### Interact
Get your bot to a public channel, then you or someone else give emoji reactions to your messages.

## Configuring the LED
TODO