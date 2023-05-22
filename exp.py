import requests

def get_order_book(symbol, depth=5):
    url = f"https://api.bitget.com/data/v1/market/depth?symbol={symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching order book: {response.status_code}")

symbol = "btc_usdt"  # Замените на нужную торговую пару
order_book = get_order_book(symbol)
print(order_book)