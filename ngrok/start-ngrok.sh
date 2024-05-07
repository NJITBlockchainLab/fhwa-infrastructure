#!/bin/bash

if [ "$OSTYPE" == "msys" ]; then
  NGROK="winpty ngrok"
else
  NGROK="ngrok"
fi

if [ -f .env ]; then
  source .env
fi

$NGROK start --all --config=./ngrok.yml --authtoken=${NGROK_AUTH_TOKEN} --log=stdout
