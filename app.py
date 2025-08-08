from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# import ccxt  # Will be installed separately if needed
import requests
import sqlite3
import threading
import time
import json

app = Flask(__name__)

class TradingBot:
    def __init__(self):
        self.exchange = None
        self.scanner_active = False
        self.auto_trading = False
        self.telegram_token = ""
        self.telegram_chat_id = ""
        
    def init_exchange(self, api_key, secret):
        # Mock exchange for demo
        self.exchange = {
            'apiKey': api_key,
            'secret': secret,
            'connected': True
        }
    
    def backtest(self, symbol, start_date, end_date, balance, leverage, strategy_params):
        # Simplified backtest logic
        trades = []
        current_balance = balance
        
        # Mock backtest results
        for i in range(10):
            profit = np.random.uniform(-50, 100)
            current_balance += profit
            trades.append({
                'date': start_date + timedelta(days=i),
                'symbol': symbol,
                'side': 'long' if profit > 0 else 'short',
                'profit': profit,
                'balance': current_balance
            })
        
        return {
            'trades': trades,
            'final_balance': current_balance,
            'total_profit': current_balance - balance,
            'win_rate': len([t for t in trades if t['profit'] > 0]) / len(trades) * 100
        }
    
    def scan_signals(self):
        while self.scanner_active:
            # Mock signal detection
            signals = self.detect_signals()
            for signal in signals:
                self.send_telegram_alert(signal)
            time.sleep(60)
    
    def detect_signals(self):
        # Mock signal detection
        pairs = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        signals = []
        
        for pair in pairs:
            if np.random.random() > 0.95:  # 5% chance of signal
                signals.append({
                    'symbol': pair,
                    'side': 'long' if np.random.random() > 0.5 else 'short',
                    'price': np.random.uniform(20000, 50000),
                    'timestamp': datetime.now()
                })
        
        return signals
    
    def send_telegram_alert(self, signal):
        if not self.telegram_token or not self.telegram_chat_id:
            return
            
        message = f"🚨 Signal Alert\n"
        message += f"Symbol: {signal['symbol']}\n"
        message += f"Side: {signal['side'].upper()}\n"
        message += f"Price: ${signal['price']:.2f}\n"
        message += f"Time: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            'chat_id': self.telegram_chat_id,
            'text': message
        }
        requests.post(url, data=data)
    
    def optimize_parameters(self, symbol, historical_data):
        # Mock optimization
        best_params = {
            'tp_percentage': np.random.uniform(1, 5),
            'sl_percentage': np.random.uniform(0.5, 2),
            'rsi_period': np.random.randint(10, 20),
            'ma_period': np.random.randint(20, 50)
        }
        return best_params

bot = TradingBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backtest', methods=['POST'])
def backtest():
    data = request.json
    result = bot.backtest(
        data['symbol'],
        datetime.strptime(data['start_date'], '%Y-%m-%d'),
        datetime.strptime(data['end_date'], '%Y-%m-%d'),
        float(data['balance']),
        float(data['leverage']),
        data.get('strategy_params', {})
    )
    return jsonify(result)

@app.route('/scanner/start', methods=['POST'])
def start_scanner():
    bot.scanner_active = True
    scanner_thread = threading.Thread(target=bot.scan_signals)
    scanner_thread.daemon = True
    scanner_thread.start()
    return jsonify({'status': 'Scanner started'})

@app.route('/scanner/stop', methods=['POST'])
def stop_scanner():
    bot.scanner_active = False
    return jsonify({'status': 'Scanner stopped'})

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    result = bot.optimize_parameters(data['symbol'], data.get('historical_data'))
    return jsonify(result)

@app.route('/config', methods=['POST'])
def update_config():
    data = request.json
    bot.telegram_token = data.get('telegram_token', '')
    bot.telegram_chat_id = data.get('telegram_chat_id', '')
    
    if data.get('api_key') and data.get('secret'):
        bot.init_exchange(data['api_key'], data['secret'])
    
    return jsonify({'status': 'Config updated'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)