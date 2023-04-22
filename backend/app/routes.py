from app import app
from flask import jsonify, request, Response
import json
import yfinance as yf
from twilio.rest import Client
from flask_mail import Mail, Message
import dotenv
import os

dotenv.load_dotenv()

global subscribers
account_sid = os.getenv("TWILIO_ID")
auth_token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("MAIL_ID")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def send_message(contactValue):
    message = client.messages.create(
        body='Your stock price has reached the threshold!',
        from_='9844653868',
        to=contactValue
    )

def send_email(contactValue):
    msg = Message('Hello from Flask!', 
                  sender=os.getenv("MAIL_ID"), 
                  recipients=[contactValue])
    msg.body = "Your stock has reached a threshold"
    mail.send(msg)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        data = request.get_json()
        # request_data = json.loads(data.decode('utf-8'))
        global subscribers
        subscribers = data
        print (subscribers)
        return jsonify({'message': 'Subscribed'})
    else:
        return jsonify({'message': 'Error'})
#contactType,
    #   contactValue,
    #   stockTicker,
    #   threshold,


@app.route('/getstock', methods=['GET'])
def getstock():
    global subscribers
    print (subscribers)
    stock = yf.Ticker(subscribers['stockTicker'])
    print (stock.info)
    if stock.info['currentPrice'] > subscribers['threshold']:
        if subscribers['contactType'] == 'email':
            send_email(subscribers['contactValue'])
        elif subscribers['contactType'] == 'phone':
            send_message(subscribers['contactValue'])
    print (stock.info)
    return jsonify(stock.info)

