import base64
import datetime
import json
import os

import openai
import vosk
from dotenv import load_dotenv
from flask import Flask, request
from flask_sock import ConnectionClosed, Sock
from twilio.rest import Client
from twilio.twiml.voice_response import Start, VoiceResponse

load_dotenv()

import openai
import requests
openai.api_key = os.environ["OPENAI_API_KEY"]

url = "http://127.0.0.1:5000/make_call"


user_prompt = input("Enter your prompt: ")
messages: list[dict[str, str]] = [
    {"role": "user", "content": 
    "Output one word containing LOCATION for the location of the spot where the user wants to order pizza from. The possible LOCATION are: 'PizzaPizza', 'PizzaNova', 'Dominos'. Make sure you keep capitlization and type exactly as before!!"},
    {"role": "user", "content": user_prompt}
]

phone_numbers = {
    'PizzaNova': '+18443103300',
    'Dominos': '+15197452222',
    'PizzaPizza': '+15197471111',
}

# phone_numbers = {
#     'PizzaNova': '12365187890',
#     'Dominos': '12365187890',
#     'PizzaPizza': '12365187890',
# }
response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )

location = response["choices"][0]["message"]["content"]
phone = phone_numbers[location]
print(response)
print(url + f'?location={location}&phone={phone}')
requests.get(url + f'?location={location}&phone={phone}')