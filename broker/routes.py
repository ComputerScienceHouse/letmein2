from app import config
from flask import render_template
from flask import request
from flask_socketio import *
from app import app
import time
import sys
import atexit
import json
import requests
from urllib.parse import urlencode
from urllib.request import urlopen
from os import curdir,sep
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SITE_VERIFY_URL = config.RECAPTCHA_SITE_VERIFY_URL
SECRET_KEY = config.RECAPTCHA_SECRET_KEY

SLACK = WebClient(config.SLACK_KEY)

SOCKETIO = SocketIO(app)

BUSY = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activate', methods=['POST'])
def activate():
    body = request.json
    RECAPTCHA_RESPONSE = body['response']

    REMOTE_IP = request.remote_addr
    params = urlencode({
        'secret':SECRET_KEY,
        'response':RECAPTCHA_RESPONSE,
    })

    data = urlopen(SITE_VERIFY_URL, params.encode('utf-8')).read()

    result = json.loads(data)
    success = result.get('success', None)

    if success:
        global BUSY
        BUSY = True
        level = body['level']
        startTime = time.time()

        print("Activating: " + level, file=sys.stderr)

        SOCKETIO.emit('letmein',{'location':level}, to='nrh3')
        while True:
            elapsedTime = time.time() - startTime
            timedOut = elapsedTime > 45
            if timedOut or not BUSY:
                if timedOut:
                    print("Button timed out", file=sys.stderr)
                    SOCKETIO.emit('ack', {'location',level}, to='nrh3')
                    return "timeout"
                elif not BUSY:
                    print("Button pressed", file=sys.stderr)
                    return "buttonpressed"
                return ""
    else:
        return "not verified"

@app.route('/notify', methods=['POST'])
def notify_slack():
    body = request.json
    text = body['text']
    WebClient.chat_postMessage(channel = "CCN6USBTQ", text=text)
    return "notification posted"

def shutdown():
    print("Goodbye", file=sys.stderr)

@SOCKETIO.on('connect')
def connect():
    join_room('nrh3')

@SOCKETIO.on('ack')
def ack(data):
    global BUSY
    BUSY=False

atexit.register(shutdown)

