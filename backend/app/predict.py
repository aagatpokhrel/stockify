import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler 
from tensorflow import keras
from tensorflow.keras import layers

def predict_stock(hist):
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

    # Get the last 60 days of closing prices
    last_60_days = hist['Close'][-60:].values.reshape(-1, 1)
    last_60_days_scaled = scaler.transform(last_60_days)
    future_predictions = []
    for i in range(30):
        X_test = np.reshape(last_60_days_scaled, (1, last_60_days_scaled.shape[0], 1))
        y_pred = model.predict(X_test)
        y_pred_actual = scaler.inverse_transform(y_pred)
        future_predictions.append(y_pred_actual[0][0])
        last_60_days_scaled = np.vstack([last_60_days_scaled[1:], y_pred])
    return future_predictions