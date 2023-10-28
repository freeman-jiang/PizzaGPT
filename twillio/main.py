# Download the helper library from https://www.twilio.com/docs/python/install
import audioop
import base64
import datetime
import json
import os

import openai
import transcribe
import vosk
from dotenv import load_dotenv
from flask import Flask, request
from flask_sock import ConnectionClosed, Sock
from twilio.rest import Client
from twilio.twiml.voice_response import Start, VoiceResponse

load_dotenv()

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
number_to_call = os.environ["TO_PHONE_NUMBER"]
openai.api_key = os.environ["OPENAI_API_KEY"]


twilio_client = Client(account_sid, auth_token)


# print(call.sid)

app = Flask(__name__)
sock = Sock(app)
model = vosk.Model('model')

CL = '\x1b[0K'
BS = '\x08'

say_queue = []

host = ""


@app.route('/')
def health_check():
    """Health check."""
    return 'OK'


@app.route('/call', methods=['POST'])
def call():
    global host
    """Accept a phone call."""
    response = VoiceResponse()
    start = Start()
    host = request.host

    # Call the stream
    start.stream(url=f'wss://{request.host}/stream')
    response.append(start)
    response.say('Please leave a message')
    response.pause(length=60)
    print(f'Incoming call from {request.form["From"]}')
    return str(response), 200, {'Content-Type': 'text/xml'}


concat_response = ""
last_processed: datetime.datetime = datetime.datetime.now()
messages: list[dict[str, str]] = [
    {"role": "system", "content": "Pretend you are a person at Communitech, which is at 151 Charles St W Suite 100, Kitchener, ON N2G 1H6. Your only objective is to order a 14-inch cheese pizza to 151 Charles St W Suite 100, Kitchener, ON N2G 1H6. You are on the phone. You will pay by cash later. Answer the pizza operator as succinctly as you can"},
]


@sock.route('/stream')
def stream(ws):
    global concat_response
    global last_processed
    global messages
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

            # print("WHISPER: ", transcribe.transcribe(audio))

            if rec.AcceptWaveform(audio):
                r = json.loads(rec.Result())
                voice_response = r['text']
                print(f"Collecting response {voice_response}")

                concat_response += f" {voice_response}"

                time_difference = datetime.datetime.now() - last_processed
                if time_difference.total_seconds() <= 3:
                    continue
                # Only after 5 seconds, send the message to open ai

                # Here's what I want to do. I do not want to spam the chat bot with many messages.
                # You should concatenate the messages and every 5 seconds, send the whole message to open ai

                messages.append({"role": "user", "content": concat_response})
                generated_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )

                response_message = generated_response["choices"][0]["message"]["content"]
                messages.append(
                    {"role": "assistant",  "content": response_message})

                print(f"GPT response demo: {response_message}")
                twilio_client.calls(call_id).update(twiml=f"""<Response>
                                                                  <Say> {response_message} </Say>
                                                                  <Start>
                                                                    <Stream url="wss://{host}/stream" />
                                                                  </Start>
                                                                  <Pause length="60" />
                                                                  </Response>
                                                                  """)
                last_processed = datetime.datetime.now()
                break
                # print(CL + r['text'] + ' ', end='', flush=True)

            else:
                r = json.loads(rec.PartialResult())
                print(CL + r['partial'] + BS *
                      len(r['partial']), end='', flush=True)
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
        to=number_to_call,  # Replace with the desired 'to' number
        from_=twilio_phone_number,  # Your Twilio phone number
        url=public_url + '/call',
    )

    global call_id
    call_id = call.sid
    return call.sid


if __name__ == '__main__':
    from pyngrok import ngrok
    port = 5000
    public_url = ngrok.connect(port, bind_tls=True).public_url
    number = twilio_client.incoming_phone_numbers.list()[0]
    number.update(voice_url=public_url + '/call')

    print(f'Waiting for calls  {number.phone_number}')
    print(f"Listening for audio on {public_url}")
    app.run(port=port)
