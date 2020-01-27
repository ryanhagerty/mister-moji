#!/bin/bash
echo "Installing RGB Matrix and Slackbot and dependencies. This may take some time (10-20 minutes-ish)..."
git submodule update --init
cd matrix
sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
make build-python
sudo make install-python
cd bindings
sudo pip install -e python/
cd ../../
sudo pip install virtualenv
virtualenv env
source env/bin/activate
sudo pip install slackclient
sudo pip install slackeventsapi
sudo apt-get install libxml2-dev libxslt-dev
sudo pip install requests
echo "Installation complete! 😃"