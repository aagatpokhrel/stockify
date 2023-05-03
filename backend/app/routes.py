from app import app
from flask import jsonify, request, Response
import json
import yfinance as yf
from twilio.rest import Client
import requests
import dotenv
import os

import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler 
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
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
        stock = yf.Ticker(subscribers['stockTicker'])
        hist = stock.history(period="12mo")
        values = hist['Close'].values
        training_data_len = math.ceil(len(values)* 0.8)

        # scale data using MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(values.reshape(-1,1))

        # split data into training and testing sets
        train_data = scaled_data[0: training_data_len, :]
        x_train = []
        y_train = []
        for i in range(60, len(train_data)):
            x_train.append(train_data[i-60:i, 0])
            y_train.append(train_data[i, 0])
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        test_data = scaled_data[training_data_len-60: , : ]
        x_test = []
        y_test = values[training_data_len:]
        for i in range(60, len(test_data)):
            x_test.append(test_data[i-60:i, 0])
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        # build and train model
        model = keras.Sequential()
        model.add(layers.GRU(100, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(layers.Dropout(0.2))
        model.add(layers.GRU(100, return_sequences=False))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(25))
        model.add(layers.Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, batch_size=1, epochs=10)

    # To predict the data
        predictions = model.predict(x_test)
        predictions = scaler.inverse_transform(predictions)
        rmse = np.sqrt(np.mean(predictions - y_test)**2)

        data = hist.filter(['Close'])
        train = data[:training_data_len]
        validation = data[training_data_len:]
        validation['Predictions'] = predictions
        
        fig,ax = plt.subplots(figsize=(16,8))
        ax.set_title('Model')
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price')
        ax.plot(train)
        ax.plot(validation[['Last_tp', 'Predictions']])
        ax.legend(['Train', 'Val', 'Predictions'], loc='lower right')
        ax.set_xticklabels(df_data['Dates'])
        plt.xticks(rotation=45)

        # Get the last 60 days of closing prices
        last_60_days = df_data['Last_tp'][-60:].values.reshape(-1, 1)
        last_60_days_scaled = scaler.transform(last_60_days)
        future_predictions = []
        for i in range(30):
            X_test = np.reshape(last_60_days_scaled, (1, last_60_days_scaled.shape[0], 1))
            y_pred = model.predict(X_test)
            y_pred_actual = scaler.inverse_transform(y_pred)
            future_predictions.append(y_pred_actual[0][0])
            last_60_days_scaled = np.vstack([last_60_days_scaled[1:], y_pred])

        # Plot the predicted values
        
        fig,ax = plt.subplots(figsize=(16,8))
        ax.plot(df_data['Last_tp'])
        ax.plot(np.arange(len(df_data['Last_tp']), len(df_data['Last_tp']) + len(future_predictions)), future_predictions)
        ax.set_title('Predicted Stock Prices')
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price')
        ax.legend(['Actual', 'Predicted'])
        ax.set_xticklabels(df_data['Dates'])
        plt.xticks(rotation=45)
        fig.savefig(f'{symbol}future_data_graph.png')
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

