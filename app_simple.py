from flask import Flask, render_template, request, jsonify
import json
import random
from datetime import datetime, timedelta
import threading
import time
from free_api import FreeDataProvider

app = Flask(__name__)

class TradingBot:
    def __init__(self):
        self.scanner_active = False
        self.telegram_token = ""
        self.telegram_chat_id = ""
        self.data_provider = FreeDataProvider()
        
    def backtest(self, symbol, start_date, end_date, balance, leverage):
        days = (end_date - start_date).days
        historical_data = self.data_provider.get_historical_data(symbol, days)
        
        trades = []
        open_positions = []
        current_balance = balance
        position = None
        
        for i, data in enumerate(historical_data[1:], 1):
            prev_data = historical_data[i-1]
            current_price = data['close']
            
            # Close existing position if TP/SL hit
            if position:
                should_close = False
                exit_reason = ""
                
                if position['side'] == 'long':
                    if current_price >= position['tp_price']:
                        should_close = True
                        exit_reason = "TP Hit"
                    elif current_price <= position['sl_price']:
                        should_close = True
                        exit_reason = "SL Hit"
                elif position['side'] == 'short':
                    if current_price <= position['tp_price']:
                        should_close = True
                        exit_reason = "TP Hit"
                    elif current_price >= position['sl_price']:
                        should_close = True
                        exit_reason = "SL Hit"
                
                if should_close:
                    if position['side'] == 'long':
                        profit = (current_price - position['entry_price']) * position['size']
                    else:
                        profit = (position['entry_price'] - current_price) * position['size']
                    
                    current_balance += profit
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': datetime.fromtimestamp(data['timestamp']/1000).strftime('%Y-%m-%d %H:%M'),
                        'symbol': symbol,
                        'side': position['side'],
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'size': position['size'],
                        'profit': profit,
                        'balance': current_balance,
                        'exit_reason': exit_reason,
                        'duration_hours': int((data['timestamp'] - position['entry_timestamp']) / (1000 * 3600))
                    })
                    position = None
            
            # Open new position on signal
            if not position:
                signal = False
                side = None
                
                # Long signal: 3% price increase
                if current_price > prev_data['close'] * 1.03:
                    signal = True
                    side = 'long'
                # Short signal: 3% price decrease  
                elif current_price < prev_data['close'] * 0.97:
                    signal = True
                    side = 'short'
                
                if signal:
                    position_size = (current_balance * leverage * 0.1) / current_price  # 10% of balance
                    
                    position = {
                        'side': side,
                        'entry_price': current_price,
                        'entry_date': datetime.fromtimestamp(data['timestamp']/1000).strftime('%Y-%m-%d %H:%M'),
                        'entry_timestamp': data['timestamp'],
                        'size': position_size,
                        'tp_price': current_price * (1.02 if side == 'long' else 0.98),  # 2% TP
                        'sl_price': current_price * (0.99 if side == 'long' else 1.01)   # 1% SL
                    }
                    
                    open_positions.append({
                        'date': position['entry_date'],
                        'symbol': symbol,
                        'side': side,
                        'entry_price': current_price,
                        'size': position_size,
                        'tp_price': position['tp_price'],
                        'sl_price': position['sl_price'],
                        'status': 'Open'
                    })
        
        # Close any remaining open position
        if position:
            current_price = historical_data[-1]['close']
            if position['side'] == 'long':
                profit = (current_price - position['entry_price']) * position['size']
            else:
                profit = (position['entry_price'] - current_price) * position['size']
            
            current_balance += profit
            trades.append({
                'entry_date': position['entry_date'],
                'exit_date': datetime.fromtimestamp(historical_data[-1]['timestamp']/1000).strftime('%Y-%m-%d %H:%M'),
                'symbol': symbol,
                'side': position['side'],
                'entry_price': position['entry_price'],
                'exit_price': current_price,
                'size': position['size'],
                'profit': profit,
                'balance': current_balance,
                'exit_reason': 'End of Period',
                'duration_hours': int((historical_data[-1]['timestamp'] - position['entry_timestamp']) / (1000 * 3600))
            })
        
        winning_trades = [t for t in trades if t['profit'] > 0]
        losing_trades = [t for t in trades if t['profit'] <= 0]
        
        return {
            'trades': trades,
            'open_positions': open_positions,
            'final_balance': current_balance,
            'total_profit': current_balance - balance,
            'win_rate': len(winning_trades) / len(trades) * 100 if trades else 0,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_profit': sum(t['profit'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            'max_profit': max([t['profit'] for t in trades]) if trades else 0,
            'max_loss': min([t['profit'] for t in trades]) if trades else 0
        }
    
    def scan_signals(self):
        while self.scanner_active:
            # Get real-time prices and detect signals
            top_cryptos = self.data_provider.get_top_cryptos()
            
            for crypto in top_cryptos[:5]:  # Check top 5
                if abs(crypto['change_24h']) > 5:  # Significant movement
                    signal = {
                        'symbol': crypto['symbol'],
                        'side': 'long' if crypto['change_24h'] > 0 else 'short',
                        'price': crypto['price'],
                        'change': crypto['change_24h']
                    }
                    print(f"Signal detected: {signal}")
            
            time.sleep(300)  # Check every 5 minutes
    
    def optimize_parameters(self, symbol):
        return {
            'tp_percentage': random.uniform(1, 5),
            'sl_percentage': random.uniform(0.5, 2),
            'rsi_period': random.randint(10, 20),
            'ma_period': random.randint(20, 50)
        }

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
        float(data['leverage'])
    )
    return jsonify(result)

@app.route('/scanner/start', methods=['POST'])
def start_scanner():
    bot.scanner_active = True
    return jsonify({'status': 'Scanner started'})

@app.route('/scanner/stop', methods=['POST'])
def stop_scanner():
    bot.scanner_active = False
    return jsonify({'status': 'Scanner stopped'})

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    result = bot.optimize_parameters(data['symbol'])
    return jsonify(result)

@app.route('/config', methods=['POST'])
def update_config():
    data = request.json
    bot.telegram_token = data.get('telegram_token', '')
    bot.telegram_chat_id = data.get('telegram_chat_id', '')
    return jsonify({'status': 'Config updated'})

@app.route('/crypto-prices')
def get_crypto_prices():
    prices = bot.data_provider.get_top_cryptos()
    return jsonify(prices)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)