import os
from twilio.rest import Client
from dotenv import load_dotenv
import audioop
import base64
import json
import asyncio
from flask import Flask, request
import websockets  # You may need to install this library
from twilio.twiml.voice_response import VoiceResponse, Start
import vosk

load_dotenv()

# Set environment variables for your credentials
account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")
twilio_client = Client(account_sid, auth_token)

app = Flask(__name)
model = vosk.Model('model')

CL = '\x1b[0K'
BS = '\x08'

# WebSocket connection to Twilio
async def twilio_websocket():
    uri = f'wss://your-twilio-domain/call/stream'  # Replace with your Twilio domain
    async with websockets.connect(uri) as ws:
        rec = vosk.KaldiRecognizer(model, 16000)
        while True:
            message = await ws.recv()
            packet = json.loads(message)
            if packet['event'] == 'start':
                print('Streaming is starting')
            elif packet['event'] == 'stop':
                print('\nStreaming has stopped')
            elif packet['event'] == 'media':
                audio = base64.b64decode(packet['media']['payload'])
                audio = audioop.ulaw2lin(audio, 2)
                audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
                if rec.AcceptWaveform(audio):
                    r = json.loads(rec.Result())
                    print(CL + r['text'] + ' ', end='', flush=True)
                    # Send your response back to Twilio through the WebSocket here
                    await ws.send(response_audio_data)  # Replace with actual response data

# Define a route to initiate the call
@app.route('/make_call', methods=['GET'])
def make_call():
    """Initiate a call from Twilio."""
    call = twilio_client.calls.create(
        to="+16044411171",  # Replace with the desired 'to' number
        from_="+17326540954",  # Your Twilio phone number
        url=f"{public_url}/call",  # Use your existing '/call' URL
    )
    return call.sid

public_url = ""
if __name__ == '__main__':
    from pyngrok import ngrok
    port = 5000
    public_url = ngrok.connect(port, bind_tls=True).public_url
    number = twilio_client.incoming_phone_numbers.list()[0]
    number.update(voice_url=public_url + '/call')

    print(f'Waiting for calls on {number.phone_number}')
    print(public_url)

    asyncio.get_event_loop().run_until_complete(twilio_websocket())  # Start the WebSocket connection
