import requests
import time
from datetime import datetime, timedelta

class FreeDataProvider:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.alpha_vantage_key = "demo"  # Free demo key
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
    
    def get_crypto_price(self, symbol):
        """Get current price from CoinGecko (Free)"""
        try:
            # Convert BTCUSDT to bitcoin format
            coin_map = {
                'BTCUSDT': 'bitcoin',
                'ETHUSDT': 'ethereum', 
                'ADAUSDT': 'cardano',
                'BNBUSDT': 'binancecoin',
                'SOLUSDT': 'solana',
                'XRPUSDT': 'ripple',
                'DOGEUSDT': 'dogecoin'
            }
            
            coin_id = coin_map.get(symbol, 'bitcoin')
            url = f"{self.coingecko_base}/simple/price"
            params = {'ids': coin_id, 'vs_currencies': 'usd'}
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return data[coin_id]['usd']
        except:
            return 50000  # Mock price if API fails
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data from CoinGecko (Free)"""
        try:
            coin_map = {
                'BTCUSDT': 'bitcoin',
                'ETHUSDT': 'ethereum',
                'ADAUSDT': 'cardano'
            }
            
            coin_id = coin_map.get(symbol, 'bitcoin')
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            
            response = requests.get(url, params=params)
            data = response.json()
            
            # Convert to OHLCV format
            prices = data['prices']
            ohlcv_data = []
            
            for i in range(0, len(prices), 24):  # Daily data
                if i + 23 < len(prices):
                    day_prices = [p[1] for p in prices[i:i+24]]
                    ohlcv_data.append({
                        'timestamp': prices[i][0],
                        'open': day_prices[0],
                        'high': max(day_prices),
                        'low': min(day_prices),
                        'close': day_prices[-1],
                        'volume': 1000000  # Mock volume
                    })
            
            return ohlcv_data
        except:
            # Return mock data if API fails
            return self._generate_mock_data(days)
    
    def get_top_cryptos(self):
        """Get top cryptocurrencies (Free)"""
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 20,
                'page': 1
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return [{
                'symbol': coin['symbol'].upper() + 'USDT',
                'name': coin['name'],
                'price': coin['current_price'],
                'change_24h': coin['price_change_percentage_24h']
            } for coin in data]
        except:
            return [
                {'symbol': 'BTCUSDT', 'name': 'Bitcoin', 'price': 50000, 'change_24h': 2.5},
                {'symbol': 'ETHUSDT', 'name': 'Ethereum', 'price': 3000, 'change_24h': 1.8}
            ]
    
    def _generate_mock_data(self, days):
        """Generate mock OHLCV data"""
        data = []
        base_price = 50000
        
        for i in range(days):
            change = (random.random() - 0.5) * 0.1  # ±5% change
            base_price *= (1 + change)
            
            data.append({
                'timestamp': int((datetime.now() - timedelta(days=days-i)).timestamp() * 1000),
                'open': base_price * 0.99,
                'high': base_price * 1.02,
                'low': base_price * 0.98,
                'close': base_price,
                'volume': 1000000
            })
        
        return data

# Alternative APIs you can use:
class AlternativeAPIs:
    """
    Other free crypto APIs:
    
    1. CryptoCompare (Free tier: 100k calls/month)
       - https://min-api.cryptocompare.com/
    
    2. CoinAPI (Free tier: 100 calls/day)  
       - https://rest.coinapi.io/
    
    3. Messari (Free tier: 1000 calls/month)
       - https://data.messari.io/api/
    
    4. CoinCap (Free, unlimited)
       - https://api.coincap.io/v2/
    
    5. Nomics (Free tier: 1 call/sec)
       - https://api.nomics.com/v1/
    """
    
    def get_coincap_price(self, symbol):
        """CoinCap API - Free unlimited"""
        try:
            asset_map = {'BTCUSDT': 'bitcoin', 'ETHUSDT': 'ethereum'}
            asset = asset_map.get(symbol, 'bitcoin')
            
            url = f"https://api.coincap.io/v2/assets/{asset}"
            response = requests.get(url)
            data = response.json()
            
            return float(data['data']['priceUsd'])
        except:
            return 50000