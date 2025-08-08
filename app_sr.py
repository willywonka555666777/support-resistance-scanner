from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from support_resistance_simple import SupportResistanceAnalyzer
import threading
import time

app = Flask(__name__)
analyzer = SupportResistanceAnalyzer()
scanning = False
scan_thread = None

@app.route('/')
def index():
    return render_template('sr_index.html')

@app.route('/scan-opportunities')
def scan_opportunities():
    global scanning
    max_support_dist = request.args.get('support_dist', 5, type=float)
    max_resistance_dist = request.args.get('resistance_dist', 3, type=float)
    timeframes = request.args.get('timeframes', '').split(',') if request.args.get('timeframes') else None
    
    scanning = True
    opportunities = analyzer.scan_all_coins(max_support_dist, max_resistance_dist, timeframes, not scanning)
    scanning = False
    return jsonify(opportunities)

@app.route('/stop-scan', methods=['POST'])
def stop_scan():
    global scanning
    scanning = False
    return jsonify({'status': 'Scan stopped'})

@app.route('/analyze-coin/<coin_id>')
def analyze_coin(coin_id):
    timeframes = request.args.get('timeframes', '').split(',') if request.args.get('timeframes') else None
    
    # Get coin info first
    coins = analyzer.get_top_coins(100)
    coin_info = next((c for c in coins if c['id'] == coin_id), None)
    
    if not coin_info:
        return jsonify({'error': 'Coin not found'})
    
    analysis = analyzer.analyze_coin(coin_id, coin_info['name'], coin_info['symbol'], timeframes)
    return jsonify(analysis)

@app.route('/get-coins')
def get_coins():
    coins = analyzer.get_top_coins(50)
    result = []
    for coin in coins:
        result.append({
            'id': coin['id'],
            'name': coin['name'], 
            'symbol': coin['symbol'].upper(),
            'price': coin['current_price'],
            'change_24h': coin['price_change_percentage_24h']
        })
    return jsonify(result)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)