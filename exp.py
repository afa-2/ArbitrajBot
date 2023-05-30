import requests
import time
import hmac
import hashlib

# Замените YOUR_API_KEY и YOUR_SECRET_KEY на свои ключи API Kukoin
api_key = '6474e1256670fc00013d648a'
secret_key = 'fe6c176a-2209-4abb-bcf8-7bc59012559c'

# Определяем параметры запроса
url = 'https://api.kucoin.com/api/v1/withdrawals/quotas'
headers = {
    'Content-Type': 'application/json',
    'KC-API-KEY': api_key,
    'KC-API-NONCE': str(int(time.time() * 1000)),
}

# Создаем подпись запроса
message = '/api/v1/withdrawals/quotas' + str(int(time.time() * 1000))
signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
headers['KC-API-SIGNATURE'] = signature

# Отправляем запрос и получаем ответ
response = requests.get(url, headers=headers)
response_json = response.json()
print(response)
