import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [contactType, setContactType] = useState('');
  const [contactValue, setContactValue] = useState('');
  const [stockTicker, setStockTicker] = useState('');
  const [threshold, setThreshold] = useState('');
  const [frequency, setFrequency] = useState('');
  const [cards, setCards] = useState([]);

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

  const handleSubmit = (event) => {
    event.preventDefault();
    axios.post('http://localhost:5000/subscribe', {
      contactType,
      contactValue,
      stockTicker,
      threshold,
    })
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const fetchStocks = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/getstock`);
        setCards(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchStocks();
    }, frequency === 'hourly' ? 3600000 : frequency === 'daily' ? 86400000 : 604800000);

    return () => clearInterval(intervalId);
  }, [frequency, stockTicker]);

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
              <option value="daily">Minutely</option>
              <option value="weekly">Hourly</option>
              <option value="monthly">Daily</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          <div className="form-group">
            <button type="submit" class="submit">Subscribe</button>
          </div>
        </form>
      </div>
      <div className="card-container">
        {cards.map((card, index) => (
          <div key={index} className="card">
            <div className="card-header">
              {card.stockTicker} - {card.threshold}
            </div>
            <div className="card-body">
              <div className="card-data">
                Last Price: {card.lastPrice}
              </div>
              <div className="card-data">
                Change: {card.change}
              </div>
              <div className="card-data">
                Date: {card.date}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
export default App;
