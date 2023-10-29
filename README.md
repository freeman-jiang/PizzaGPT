# PizzaGPT
## What it does
Hungry for pizza? Simply instruct PizzaGPT, and it will automatically place a call to a local pizzeria near you, conversing with real humans to arrange your order. 

## How we built it

Using a local Mistral-7B model, we parse the user’s request and route it to the correct phone number. Then, using ChatGPT, and a local transcription model, we talk to the pizza vendors and order a pizza as an AI agent. We use the Twilio API to make phone calls and in real-time, we transcribe the pizza operator’s voice using Vosk (locally) and generate a response using ChatGPT, which is spoken to the operator using Google’s text-to-speech service.

## Challenges we ran into
Twilio’s API was very tricky to use, especially for interactive applications. We also had lots of trouble working with streaming raw audio data. Hilariously, the AI agent also occasionally reversed its role and thought it was the pizza place instead. This resulted in some pretty funny bugs. 

We actually called six different pizza shops with PizzaGPT. But human operators would get frustrated with PizzaGPT because at first it was very verbose, so we weren’t able to actually get a pizza delivered in time. Sometimes, we had a hard time transcribing the operator’s voice and response latency could also have been improved.

Twilio also had little observability in the phone calls. We watched the terminal and prayed that PizzaGPT was doing the conversation correctly. This made it hard to debug if the problems were because of poor transcription, latency, or other factors. 

## Accomplishments that we're proud of
We’re proud that we could get an AI agent to have an interactive, real-time conversation with a pizza operator. We were also proud that we could make the LLM stay on task and speak concisely. 

## What we learned
We learned lots about how to write good prompts for the LLM to generate meaningful responses, which made a drastic difference. We also learned lots about working with audio and real-time voice applications.

## What's next for PizzaGPT
Generalize food ordering and phone calls. You can ask PizzaGPT to do anything for you, like make a customer service complaint, order pizza, or book a hotel! We all know being on hold is a PITA, so PizzaGPT should be able to do that for you.
