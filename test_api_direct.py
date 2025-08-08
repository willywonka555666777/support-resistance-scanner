import requests

# Test CoinGecko API directly
def test_coingecko():
    print("Testing CoinGecko API directly...")
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {'ids': 'bitcoin,ethereum', 'vs_currencies': 'usd'}
        
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Bitcoin: ${data['bitcoin']['usd']}")
            print(f"Ethereum: ${data['ethereum']['usd']}")
        else:
            print("API request failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_coingecko()