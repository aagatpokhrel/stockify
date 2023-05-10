import React, { PureComponent, useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

import './App.css';

function MyLineChart({ data }) {
  console.log(data)
  return (
    <LineChart
      width={500}
      height={300}
      data={data}
      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
    >
      <XAxis dataKey="date" />
      <YAxis dataKey="price"/>
      <CartesianGrid strokeDasharray="3 3" />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="price" stroke="#ffffff" />
    </LineChart>
  );
}


function App() {
  const [contactType, setContactType] = useState('');
  const [contactValue, setContactValue] = useState('');
  const [stockTicker, setStockTicker] = useState('');
  const [threshold, setThreshold] = useState('');
  const [frequency, setFrequency] = useState('');
  const [data, setData] = useState('');

  const handleContactTypeChange = (event) => {
    setContactType(event.target.value);
    setContactValue('');
  };

  const handleContactValueChange = (event) => {
    setContactValue(event.target.value);
  };

  const handleStockTickerChange = (event) => {
    setStockTicker(event.target.value);
  };

  const handleThresholdChange = (event) => {
    setThreshold(event.target.value);
  };

  const handleFrequencyChange = (event) => {
    setFrequency(event.target.value);
  };

  const frequency_map=  {
    'hourly': 3600000,
    'daily': 86400000,
    'monthly': 2592000000,
    'quarterly': 7776000000,
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    var frequency_val = frequency_map[frequency];
    axios.post('http://localhost:5000/subscribe', {
      contactType,
      contactValue,
      stockTicker,
      threshold,
      frequency_val,
    })
      .then((response) => {
        var modified_data = JSON.parse(response.data['stock_hist']).map((d, i) => {
          return { date: i.toString(), price: d };
        });
        setData(modified_data)
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <div className="App">
      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <h2>Notify</h2>
          <div className="form-group">
            <label>Contact Type:</label>
            <div className="radio-group">
              <div className="radio-option">
                <input
                  type="radio"
                  id="phone"
                  name="contactType"
                  value="phone"
                  checked={contactType === 'phone'}
                  onChange={handleContactTypeChange}
                />
                <label htmlFor="phone">Phone Number</label>
              </div>
              <div className="radio-option">
                <input
                  type="radio"
                  id="email"
                  name="contactType"
                  value="email"
                  checked={contactType === 'email'}
                  onChange={handleContactTypeChange}
                />
                <label htmlFor="email">Email</label>
              </div>
            </div>
          </div>
          {contactType && (
            <div className="form-group">
              <label>Contact Value:</label>
              <input
                type={contactType === 'phone' ? 'tel' : 'email'}
                value={contactValue}
                onChange={handleContactValueChange}
              />
            </div>
          )}
          <div className="form-group">
            <label>Stock Ticker:</label>
            <input type="text" value={stockTicker} onChange={handleStockTickerChange} />
          </div>
          <div className="form-group">
            <label>Threshold:</label>
            <input type="number" step="0.01" value={threshold} onChange={handleThresholdChange} />
          </div>
          <div className="form-group">
            <label>Frequency:</label>
            <select value={frequency} onChange={handleFrequencyChange}>
              <option value="">Select Frequency</option>
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
            </select>
          </div>
          <div className="form-group">
            <button type="submit" class="submit">Subscribe</button>
          </div>
        </form>
      </div>
      <div className="chart-container">
        <MyLineChart data={data} />
      </div>
    </div>
  );
}
export default App;
