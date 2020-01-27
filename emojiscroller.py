#!/usr/bin/env python
import time
from PIL import Image
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import json
import requests
import os.path

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from utils import args, led_matrix_options

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)

class EmojiScroller:
    def __init__(self, matrix):
        self.matrix = matrix
        self.canvas = matrix.CreateFrameCanvas()
        # Slack tokens - don't commit these.
        self.slack_signing_secret = "XXXX"
        self.slack_bot_oauth_token = "XXXX"
        slack_bot_token = "XXXX"
        slack_client = SlackClient(slack_bot_token)

    def run(self):
        self.double_buffer = self.matrix.CreateFrameCanvas()
        # Size of your LED panel
        self.canvas_width = 64
        # Centers emoji: (LED panel height - image height) / 2. In this case (32 - 24) / 2. 
        self.offset_height = 4
        self.gutter = 12
        # Speed of scrolling - slower = better due to memory constraints.
        self.scroll_speed = 0.03
        self.reaction_recieved = 0
        self.font = graphics.Font()
        self.font.LoadFont("fonts/7x13.bdf")
        self.textColor = graphics.Color(255, 255, 0)
        return self

emojiscroller = EmojiScroller(matrix).run()

# Slack Event Adapter for receiving actions via the Events API
slack_events_adapter = SlackEventAdapter(
    emojiscroller.slack_signing_secret, "/slack/events")

@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    # Your Slack User ID
    # We use this to only monitor reactions to your messages
    # You can find this by uncommenting print(msgUserID) below
    myUserID = "XXXX"
    event = event_data["event"]
    eventUser = event["user"]
    emoji = event["reaction"]
    msgUserID = event["item_user"]
    #print(msgUserID)
    if msgUserID == myUserID:
        getUserData(emoji, eventUser)

def getUserData(emoji, eventUser):
    userReactingRequest = requests.get('https://slack.com/api/users.info', params={'token': emojiscroller.slack_bot_oauth_token, 'user': eventUser})
    userReactingData = userReactingRequest.json()
    userReacting = userReactingData.get('user').get('real_name')
    text = "@%s" % userReacting

    # Prevents Slack from retrying due to slow API response
    if emojiscroller.reaction_recieved == 0:
        emojiscroller.reaction_recieved += 1
        scroller(emoji, text, scroller_callback)

def scroller(emoji, text, callback = None):
    emojiImage = "images/%s.png" % emoji
    xpos = -emojiscroller.canvas_width
    count = 0
    # Try image - due to custom emojis, if the image doesn't exist, it crashes the script.
    try:
        image = Image.open(emojiImage).convert('RGB')
        while True:
            emojiscroller.double_buffer.Clear()
            textWidth = graphics.DrawText(emojiscroller.double_buffer, emojiscroller.font, -xpos, 20, emojiscroller.textColor, text)
            xpos += 1

            if (xpos > (emojiscroller.canvas_width) + (textWidth)):
                xpos = -emojiscroller.canvas_width
                count += 1
            
            emojiscroller.double_buffer.SetImage(
                # unsafe=False see:
                # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/rgbmatrix/core.pyx#L24
                # The only way to prevent overflow buffer crashes without thread/memory management.
                image, -xpos + (textWidth + emojiscroller.gutter), emojiscroller.offset_height, unsafe=False)
            emojiscroller.double_buffer = emojiscroller.matrix.SwapOnVSync(
                emojiscroller.double_buffer)

            time.sleep(emojiscroller.scroll_speed)

            if (count > 0):
                if callback != None:
                    scroller_callback()
                break
    
    # If user reacts with an image that doesn't exist (custom emoji), substitute image with reaction name.
    except:
        emojiText = " :%s:" % emoji
        userAndReactionName = text + emojiText
        while True:
            emojiscroller.double_buffer.Clear()
            textWidth = graphics.DrawText(emojiscroller.double_buffer, emojiscroller.font, -xpos, 20, emojiscroller.textColor, userAndReactionName)
            xpos += 1

            if (xpos > textWidth):
                xpos = -emojiscroller.canvas_width
                count += 1
            
            emojiscroller.double_buffer = emojiscroller.matrix.SwapOnVSync(
                emojiscroller.double_buffer)

            time.sleep(emojiscroller.scroll_speed)

            if (count > 0):
                if callback != None:
                    scroller_callback()
                break

# Prevents Slack from retrying due to slow API response
def scroller_callback():
    emojiscroller.reaction_recieved -= 1

slack_events_adapter.start(port=3000)
