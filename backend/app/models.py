from app import db
from flask_login import UserMixin
from app.predict import predict_stock

from twilio.rest import Client
import yfinance as yf

import requests
import os
import dotenv

dotenv.load_dotenv()

subscribers = None
account_sid = os.getenv("TWILIO_ID")
auth_token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)

class Subscribers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    contact_type = db.Column(db.Text)
    contact_value = db.Column(db.Text)
    stock_ticker = db.Column(db.Text)
    threshold = db.Column(db.Integer)
    frequency_val = db.Column(db.Integer)

    def __init__(self, contact_type, contact_value, stock_ticker, threshold, frequency_val):
        self.contact_type = contact_type
        self.contact_value = contact_value
        self.stock_ticker = stock_ticker
        self.threshold = threshold
        self.frequency_val = frequency_val
    
    def get_stock_hist(self):
        stock = yf.Ticker(self.stock_ticker)
        hist = stock.history(period='12mo')
        return hist
    
    def send_message(self,loss):
        if loss:
            body = "Stock Update: Your stock price is going to fall below the threshold!"
        else:
            body = "Stock Update: Your stock price is going to rise above the threshold!"

        message = client.messages.create(
            body="{}".format(body),
            from_=os.getenv("TWILIO_NUMBER"),
            to=self.contact_value
        )
    
    def send_email(self,loss):
        if loss:
            body = "Stock Update: Your stock price is going to fall below the threshold!"
        else:
            body = "Stock Update: Your stock price is going to rise above the threshold!"
        
        return requests.post(
            "https://api.mailgun.net/v3/sandboxcad704a14fe64353921c7593fe72d3e6.mailgun.org/messages",
            auth=("api", os.getenv("MAIL_KEY")),
            data={"from": "Mailgun Sandbox <postmaster@sandboxcad704a14fe64353921c7593fe72d3e6.mailgun.org>",
                "to": "{}".format(self.contact_value),
                "subject": "Stock Update",
                "text": "{}".format(body)}
        )
    
    def send_update(self):
        print ("Sending update to {}".format(self.contact_value))
        hist = self.get_stock_hist()
        future_predictions = predict_stock(hist)
        checker = (future_predictions[0] - int(self.threshold)*(hist['Close'].values[0]-int(self.threshold)))
        if (checker<0):
            if future_predictions[0] > int(self.threshold):
                loss = False
                if self.contact_type == 'email':
                    self.send_email(loss)
                elif self.contact_type == 'phone':
                    self.send_message(loss)
            if future_predictions[0] < int(self.threshold):
                loss = True
                if self.contact_type == 'email':
                    self.send_email(loss)
                elif self.contact_type == 'phone':
                    self.send_message(loss)
        else:
            pass

