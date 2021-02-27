import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from fuzzywuzzy import process

import requests
import json

# Import Flask
from flask import Flask
# Handles events from Slack
from slackeventsapi import SlackEventAdapter

# Load the Token from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configure your flask application
app = Flask(__name__)

# Configure SlackEventAdapter to handle events
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

# Using WebClient in slack, there are other clients built-in as well !!
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# connect the bot to the channel in Slack Channel
client.chat_postMessage(channel='#assignment-1', text='Bot connected')

# Get Bot ID
BOT_ID = client.api_call("auth.test")['user_id']


# handling Message Events
@slack_event_adapter.on('message')
def message(payload):
    print(payload)
    #payload is the returned json file from slack
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text2 = event.get('text')
    endChar = text2[-1]
    words = text2.split()
    if BOT_ID !=user_id and endChar=='?':
        client.chat_postMessage(channel=channel_id, text=text2)
    if BOT_ID !=user_id and words[0].lower()=='city':
        cities_list = []
        with open('cities.txt', 'r') as cities_file:
            lines = cities_file.readLines()
        for line in lines:
            cities_list.append(line)
        city = process.extractOne(text2[4:], cities_list)
        weatherResponse =requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&appid=' + os.environ['WEATHER_APPID'])
        if(weatherResponse.status_code == 200):
            weatherObject = json.loads(weatherResponse.text)
            currentTemp = round(weatherObject["main"]["temp"] - 273.15, 0)
            feelTemp = round(weatherObject["main"]["feels_like"] - 273.15, 0)
            client.chat_postMessage(channel=channel_id, text="The current temp in " + city + " is: " + str(currentTemp) + "°C and it feels like: " + str(feelTemp) + "°C")
        else:
            client.chat_postMessage(channel=channel_id, text="city does not exist")


# Run the webserver micro-service
if __name__ == "__main__":
    app.run(debug=True)