import requests
import numpy as np
from datetime import datetime, timedelta

class SupportResistanceAnalyzer:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.timeframes = {
            '15m': {'days': 1, 'interval': 'hourly'},
            '1h': {'days': 7, 'interval': 'hourly'}, 
            '4h': {'days': 30, 'interval': 'hourly'},
            '1d': {'days': 90, 'interval': 'daily'},
            '1M': {'days': 365, 'interval': 'daily'}
        }
    
    def get_coin_data(self, coin_id, timeframe):
        try:
            tf_config = self.timeframes[timeframe]
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': tf_config['days'],
                'interval': tf_config['interval']
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            prices = [p[1] for p in data['prices']]
            timestamps = [p[0] for p in data['prices']]
            
            return prices, timestamps
        except:
            return [], []
    
    def find_support_resistance(self, prices, strength=2):
        if len(prices) < 6:
            return [], []
        
        prices = np.array(prices)
        supports = []
        resistances = []
        
        # Simplified approach - find significant highs and lows
        for i in range(strength, len(prices) - strength):
            # Support: local minimum with less strict conditions
            is_support = True
            for j in range(1, strength+1):
                if prices[i] > prices[i-j] or prices[i] > prices[i+j]:
                    is_support = False
                    break
            if is_support:
                supports.append(prices[i])
            
            # Resistance: local maximum with less strict conditions
            is_resistance = True
            for j in range(1, strength+1):
                if prices[i] < prices[i-j] or prices[i] < prices[i+j]:
                    is_resistance = False
                    break
            if is_resistance:
                resistances.append(prices[i])
        
        # Add price-based levels (round numbers)
        current_price = prices[-1]
        price_levels = []
        base = int(current_price / 100) * 100  # Round to nearest 100
        for i in range(-5, 6):
            level = base + (i * 100)
            if level > 0:
                price_levels.append(level)
        
        # Combine with detected levels
        all_supports = supports + [p for p in price_levels if p < current_price]
        all_resistances = resistances + [p for p in price_levels if p > current_price]
        
        # Remove duplicates and sort
        supports = sorted(list(set([round(s, 2) for s in all_supports if s > 0])))
        resistances = sorted(list(set([round(r, 2) for r in all_resistances if r > 0])), reverse=True)
        
        return supports[-8:], resistances[:8]  # Return more levels
    
    def analyze_coin(self, coin_id, coin_name, symbol, selected_timeframes=None):
        current_price = self.get_current_price(coin_id)
        if not current_price:
            return None
            
        analysis = {
            'coin_id': coin_id,
            'name': coin_name,
            'symbol': symbol,
            'current_price': current_price,
            'timeframes': {},
            'recommendations': []
        }
        
        timeframes_to_analyze = selected_timeframes or self.timeframes.keys()
        
        for tf in timeframes_to_analyze:
            prices, timestamps = self.get_coin_data(coin_id, tf)
            if prices:
                supports, resistances = self.find_support_resistance(prices)
                
                # Find nearest support and resistance
                nearest_support = max([s for s in supports if s < current_price], default=None)
                nearest_resistance = min([r for r in resistances if r > current_price], default=None)
                
                # Calculate distances
                support_distance = ((current_price - nearest_support) / current_price * 100) if nearest_support else None
                resistance_distance = ((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else None
                
                analysis['timeframes'][tf] = {
                    'supports': supports,
                    'resistances': resistances,
                    'nearest_support': nearest_support,
                    'nearest_resistance': nearest_resistance,
                    'support_distance_pct': round(support_distance, 2) if support_distance else None,
                    'resistance_distance_pct': round(resistance_distance, 2) if resistance_distance else None
                }
        
        # Generate recommendations
        analysis['recommendations'] = self.generate_recommendations(analysis)
        return analysis
    
    def generate_recommendations(self, analysis):
        recommendations = []
        current_price = analysis['current_price']
        
        for tf, data in analysis['timeframes'].items():
            # Buy recommendation near support
            if data['support_distance_pct'] and data['support_distance_pct'] <= 3:
                entry_price = data['nearest_support'] * 1.005  # 0.5% above support
                stop_loss = data['nearest_support'] * 0.99    # 1% below support
                take_profit = current_price * 1.05            # 5% profit target
                
                recommendations.append({
                    'type': 'BUY',
                    'timeframe': tf,
                    'reason': f'Price near support level at ${data["nearest_support"]}',
                    'entry_price': round(entry_price, 4),
                    'stop_loss': round(stop_loss, 4),
                    'take_profit': round(take_profit, 4),
                    'risk_reward': round((take_profit - entry_price) / (entry_price - stop_loss), 2),
                    'confidence': 'HIGH' if data['support_distance_pct'] <= 1.5 else 'MEDIUM'
                })
            
            # Sell recommendation near resistance
            if data['resistance_distance_pct'] and data['resistance_distance_pct'] <= 2:
                entry_price = data['nearest_resistance'] * 0.995  # 0.5% below resistance
                stop_loss = data['nearest_resistance'] * 1.01     # 1% above resistance
                take_profit = current_price * 0.95               # 5% profit target
                
                recommendations.append({
                    'type': 'SELL',
                    'timeframe': tf,
                    'reason': f'Price near resistance level at ${data["nearest_resistance"]}',
                    'entry_price': round(entry_price, 4),
                    'stop_loss': round(stop_loss, 4),
                    'take_profit': round(take_profit, 4),
                    'risk_reward': round((entry_price - take_profit) / (stop_loss - entry_price), 2),
                    'confidence': 'HIGH' if data['resistance_distance_pct'] <= 1 else 'MEDIUM'
                })
        
        return recommendations
    
    def get_current_price(self, coin_id):
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {'ids': coin_id, 'vs_currencies': 'usd'}
            response = requests.get(url, params=params)
            data = response.json()
            return data[coin_id]['usd']
        except:
            return None
    
    def get_top_coins(self, limit=50):
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1
            }
            response = requests.get(url, params=params)
            return response.json()
        except:
            return []
    
    def scan_all_coins(self, max_support_distance=10, max_resistance_distance=8, selected_timeframes=None, stop_scan=False):
        coins = self.get_top_coins(20)  # Reduce to top 20 for faster scanning
        opportunities = []
        
        print(f"Scanning {len(coins)} coins...")
        
        for i, coin in enumerate(coins):
            if stop_scan:
                break
                
            print(f"Analyzing {coin['name']} ({i+1}/{len(coins)})...")
            analysis = self.analyze_coin(coin['id'], coin['name'], coin['symbol'], selected_timeframes)
            if not analysis:
                continue
                
            coin_opportunities = []
            
            for tf, data in analysis['timeframes'].items():
                # Near support (potential buy) - increased distance
                if (data['support_distance_pct'] and 
                    data['support_distance_pct'] <= max_support_distance):
                    coin_opportunities.append({
                        'type': 'SUPPORT',
                        'timeframe': tf,
                        'level': data['nearest_support'],
                        'distance_pct': data['support_distance_pct'],
                        'signal': 'BUY'
                    })
                
                # Near resistance (potential sell) - increased distance
                if (data['resistance_distance_pct'] and 
                    data['resistance_distance_pct'] <= max_resistance_distance):
                    coin_opportunities.append({
                        'type': 'RESISTANCE', 
                        'timeframe': tf,
                        'level': data['nearest_resistance'],
                        'distance_pct': data['resistance_distance_pct'],
                        'signal': 'SELL'
                    })
            
            if coin_opportunities:
                opportunities.append({
                    'coin': analysis,
                    'opportunities': coin_opportunities
                })
                print(f"Found {len(coin_opportunities)} opportunities for {coin['name']}")
        
        print(f"Scan complete. Found {len(opportunities)} coins with opportunities.")
        return opportunities