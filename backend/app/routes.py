from app import app
from flask import jsonify, request, Response
import json
import yfinance as yf
from twilio.rest import Client
import requests
import dotenv
import os

dotenv.load_dotenv()

global subscribers
account_sid = os.getenv("TWILIO_ID")
auth_token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)

def send_message(contactValue):
    message = client.messages.create(
        body="Stock Update: Your stock price has reached the threshold!",
        from_=os.getenv("TWILIO_NUMBER"),
        to=contactValue
    )
    print(message.sid)


def send_email(contactValue):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxcad704a14fe64353921c7593fe72d3e6.mailgun.org/messages",
		auth=("api", os.getenv("MAIL_KEY")),
		data={"from": "Mailgun Sandbox <postmaster@sandboxcad704a14fe64353921c7593fe72d3e6.mailgun.org>",
			"to": "{}".format(contactValue),
			"subject": "Stock Update",
			"text": "Your stock price has reached the threshold!"
        })

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        data = request.get_json()
        global subscribers
        subscribers = data
        print (subscribers)
        return jsonify({'message': 'Subscribed'})
    else:
        return jsonify({'message': 'Error'})

@app.route('/getstock', methods=['GET'])
def getstock():
    global subscribers
    stock = yf.Ticker(subscribers['stockTicker'])
    if stock.info['currentPrice'] > int(subscribers['threshold']):
        if subscribers['contactType'] == 'email':
            send_email(subscribers['contactValue'])
        elif subscribers['contactType'] == 'phone':
            send_message(subscribers['contactValue'])
    
    data = {
        "companyName": stock.info['longName'],
        "currentPrice": stock.info['currentPrice'],
        "address": stock.info['address1'],
        "industry": stock.info['industry'],
        "symbol": stock.info['symbol'],
    }
    return jsonify(data)

