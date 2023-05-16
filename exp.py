import requests

def get_order_book(symbol):
    url = f"https://api.gateio.ws/api/v4/spot/order_book?currency_pair={symbol}&limit=50"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

symbol = "BTC_USDT"
order_book = get_order_book(symbol)

if order_book:
    asks = order_book["asks"]
    bids = order_book["bids"]

    print("Asks (Sell Orders):")
    for ask in asks:
        print(f"Price: {ask[0]}, Amount: {ask[1]}")

    print("\nBids (Buy Orders):")
    for bid in bids:
        print(f"Price: {bid[0]}, Amount: {bid[1]}")