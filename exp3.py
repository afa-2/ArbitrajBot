import base64, hmac, hashlib, json, time, requests

# constants
API_KEY = "6474e1256670fc00013d648a"
API_SECRET = "fe6c176a-2209-4abb-bcf8-7bc59012559c"
API_PASSPHRASE = "eu8dKkS7LA@5LQ9"

url = "https://api.kucoin.com/api/v1/orders"

now = int(time.time() * 1000)

data = {"clientOid": "AAA", "side": "sell", "symbol": "BTC-USDT", "type": "market", "size": "0.001"}
data_json = json.dumps(data)

str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json

signature = base64.b64encode(hmac.new(API_SECRET.encode(
    'utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())

passphrase = base64.b64encode(hmac.new(API_SECRET.encode(
    'utf-8'), API_PASSPHRASE.encode('utf-8'), hashlib.sha256).digest())

headers = {
    "KC-API-SIGN": signature,
    "KC-API-TIMESTAMP": str(now),
    "KC-API-KEY": API_KEY,
    "KC-API-PASSPHRASE": passphrase,
    "KC-API-KEY-VERSION": "2",
    "Content-Type": "application/json"
}

try:
    res = requests.post(
        url, headers=headers, data=data_json).json()

    print(res)

except Exception as err:
    print(err)