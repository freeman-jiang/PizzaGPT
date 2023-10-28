# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv
import audioop
import base64
import json
from flask import Flask, request
from flask_sock import Sock, ConnectionClosed
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
import vosk
load_dotenv()

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")
twilio_client = Client(account_sid, auth_token)



# print(call.sid)

app = Flask(__name__)
sock = Sock(app)
model = vosk.Model('model')

CL = '\x1b[0K'
BS = '\x08'


@app.route('/call', methods=['POST'])
def call():
    """Accept a phone call."""
    response = VoiceResponse()
    start = Start()
    start.stream(url=f'wss://{request.host}/stream')
    response.append(start)
    response.say('Please leave a message')
    response.pause(length=60)
    print(f'Incoming call from {request.form["From"]}')
    return str(response), 200, {'Content-Type': 'text/xml'}


@sock.route('/stream')
def stream(ws):
    """Receive and transcribe audio stream."""
    rec = vosk.KaldiRecognizer(model, 16000)
    while True:
        message = ws.receive()
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
            else:
                r = json.loads(rec.PartialResult())
                print(CL + r['partial'] + BS * len(r['partial']), end='', flush=True)
# call = twilio_client.calls.create(
#   # url="http://demo.twilio.com/docs/voice.xml",
#   # to="+16044411171",
#   to="+16138794088",
#   from_="+17326540954",
# )
# response = VoiceResponse()
# start = Start()
# start.stream(url=f'wss://{request.host}/stream')
# response.append(start)
# response.say('Please leave a message')
# response.pause(length=60)
# print(f'Incoming call from {request.form["From"]}')
# return str(response), 200, {'Content-Type': 'text/xml'}

public_url = ""
@app.route('/make_call', methods=['GET'])
def make_call():
  """Initiate a call from Twilio."""
  call = twilio_client.calls.create(
      to="+16044411171",  # Replace with the desired 'to' number
      from_="+17326540954",  # Your Twilio phone number
      url=public_url + '/call', 
  )
  return call.sid

if __name__ == '__main__':
    from pyngrok import ngrok
    port = 5000
    public_url = ngrok.connect(port, bind_tls=True).public_url
    number = twilio_client.incoming_phone_numbers.list()[0]
    number.update(voice_url=public_url + '/call')

    print(f'Waiting for calls on {number.phone_number}')
    print(public_url)
    app.run(port=port)