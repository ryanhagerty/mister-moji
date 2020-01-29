# Mister Moji :sunglasses:
## An LED Panel for your Slack emoji reactions.

![User name scrolling across matrix with pizza emoji](media/matrixScrolling.gif?raw=true)

## Equipment List
Here's the parts I used to construct this. I'm linking to Adafruit, who runs out of stock a lot, but there should be equivalent parts on Amazon or what have you.
* [Raspberry Pi Zero W](https://www.adafruit.com/product/3400)
* [Micro USB Host](https://www.adafruit.com/product/1099)
* [HDMI Mini Adapter](https://www.adafruit.com/product/2819)
* [HDMI Cable](https://www.amazon.com/gp/product/B014I8SSD0)
* [5V 2.5A MicroUSB Power Supply](https://www.adafruit.com/product/1995)
* [GPIO Headers](https://www.adafruit.com/product/2822) - for a solderless version see these [GPIO Hammer Headers](https://www.adafruit.com/product/3413)
* [64x32 RGB LED Matrix - 4mm pitch](https://www.adafruit.com/product/2278)
* [RGB Matrix Bonnet](https://www.adafruit.com/product/3211)
* [5V 4A Switching Power Supply](https://www.adafruit.com/product/1466)
* [16GB MicroSD card](https://www.amazon.com/Sandisk-Ultra-Micro-UHS-I-Adapter/dp/B073K14CVB)

## Initial Setup
### Setting up your Raspberry Pi Zero
* Flash your MicroSD card with [Raspbian Buster Lite](https://www.raspberrypi.org/downloads/raspbian/). This is a minimal CLI only install of Raspbian (performance is critical for this).
* Put the card into the Zero and boot up.
* Set up [WiFi](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md) and [SSH](https://www.raspberrypi.org/documentation/remote-access/ssh/).
* Change your Zero's password: `passwd`
* [Set up a static IP address](https://www.howtogeek.com/184310/ask-htg-should-i-be-setting-static-ip-addresses-on-my-router/) for your Zero on your router.
* Confirm that you can SSH into your Zero. You can use [PuTTY](https://www.putty.org/) on Windows or the terminal on OSX/Linux.
* You can now stop using the Zero's power supply, HDMI cable and USB host. We're going to plug it directly into the bonnet, which will provide power. We will now control it entirely through SSH.

### Wire your matrix, bonnet and Zero together
* Solder the GPIO headers into the Zero. If you bought the solderless option, check out the [Adafruit page for a video tutorial](https://www.adafruit.com/product/3413) on how to hammer them in.
* Connect the bonnet to the matrix and the Zero:
  ![Matrix wiring to Raspberry Pi](media/matrixWiring.jpg?raw=true)
  * Connect the bonnet and Zero. The Zero will be underneath the bonnet.
  * Notice the alignment of the matrix in relation to the zero in this photo:
    * Connect the ribbon on the matrix to the bonnet
    * Connect one of the white connectors to the matrix. We don't need to worry about the other.
    * Connect the pitchfork connecters to the bonnet, aligning the colors so they match this photo (red positive/black negative). Tighten with a screwdriver so they don't fall out.
* Plug the Matrix power supply into the bonnet. Yea!

### Prepare for the Matrix library / install required dependencies
Once the Zero is booted up, SSH in.

* Disable on-board sound - our primary matrix library needs it:
`dtparam=audio=off` in `/boot/config.txt`

* Disable unnecessary resources like bluetooth to provide performance:
`sudo apt-get remove bluez bluez-firmware pi-bluetooth triggerhappy pigpio`

* The above tips are from the [RGB LED Matrix Troubleshooting section](https://github.com/hzeller/rpi-rgb-led-matrix#troubleshooting). Other tips are available, but I didn't need any more than those.

* Install everything:
```
sudo chmod +x install.sh
sudo ./install.sh
```

### Test your LED panel
Once your install is complete, go into `matrix/bindings/python/samples/` and paste: `sudo ./runtext.py --led-gpio-mapping=adafruit-hat`. There are other
samples in there too - play around!

If it doesn't work properly, check to ensure your wiring and headers are making good contact. If that doesn't work, check out the [RPI RGB LED Matrix](https://github.com/hzeller/rpi-rgb-led-matrix#troubleshooting) library for troubleshooting tips.

##  Setup and running the Slack portion
### Create a Slack App
Create a Slack app on https://api.slack.com/apps/

* Add a bot user to your app
* Give your bot permissions (under 'Scope' in 'OAuth and Permissions'):
  * `reactions:read`
  * `users:read`
  * `users:profile:read`
  * `channels:read`
* Install the app on your team
* Authorize the app
* Add your bot's tokens to `emojiscroller.py` located under `init`:
  You will need:
    * `SLACK_BOT_TOKEN`
    * `SLACK_SIGNING_SECRET`
    * `SLACK_BOT_OAUTH_TOKEN`

### Start ngrok
We'll use [ngrok](https://ngrok.com) so that Slack can communicate with our local server.

To start `ngrok`: `./ngrok http 3000`

Copy and paste the `https` address for your local server, then go to your Slack app and click on 'Event Subscriptions'. Enable events and paste your `ngrok` `https` address to the 'Request URL' with `/slack/events`. **Save your changes**

### Run the app
Make sure the `ngrok` server is running and type:
`sudo python emojiscroller.py --led-gpio-mapping=adafruit-hat --led-cols=64 --led-rows=32 --led-pwm-lsb-nanoseconds=280`

**Include these flags every time.** These options assume you're using the same matrix hardware as listed above.

### Get your user ID.
Follow the instructions in `emojiscroller.py` under `reaction_added` to find your user ID and add that value to the `userID` variable. Restart `emojiscroller.py`.

### Interact
Get your bot to a public channel, then you or someone else give emoji reactions to your messages.

:tada::tada::tada:

## Questions/Notes
* What about custom emojis?
You can certainly add custom emojis, and it will work. To prevent the app from failing to load a missing image, I print out the emoji name if the image doesn't exist.

* Where did you get your images?
  Oh, thanks for asking:
  * I got the images from [iamcal/emoji-data](https://github.com/iamcal/emoji-data).
  * I created a [batch action](https://design.tutsplus.com/tutorials/how-to-create-a-photoshop-batch-action--cms-32877) to convert all files to `24x24` with a black background. Because there are over 3,000 emojis, this took over 45 minutes :laughing:. Image size and transparency is a huge bottleneck when run in conjunction with the Python Slack Events API.
  * Slack only returns the emoji name instead of an ISO codepoint (like all emoji images everywhere are named). To get around this, I wrote a node script to rename and move all my images based on mapping the ISO name and the `short_name`. If you'd like to use a different set of images: Twitter, Google, etc. I put [that script up for download as well](https://github.com/ryanhagerty/unicode-slack-emoji-conversion).
  * Where are all the skin color emojis? Some system emoji sets don't support this, so it will default to the standard emoji.
