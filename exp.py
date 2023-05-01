import requests
import time
import hmac
import hashlib

api_key = 'V1IkiWjudAPBY7xsdc'
api_secret = 'fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'

def generate_signature(secret, params):
    sorted_params = sorted(params.items())
    signature_payload = '&'.join([f'{k}={v}' for k, v in sorted_params])
    return hmac.new(bytes(secret, 'utf-8'), bytes(signature_payload, 'utf-8'), hashlib.sha256).hexdigest()

def get_withdrawal_fee():
    timestamp = int(time.time() * 1000)
    params = {
        'api_key': api_key,
        'timestamp': timestamp,
    }
    params['sign'] = generate_signature(api_secret, params)

    url = 'https://api.bybit.com/v2/private/withdraw/list'
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['ret_code'] == 0:
            withdrawals = data['result']['data']
            for withdrawal in withdrawals:
                print(f"Coin: {withdrawal['coin']}, Fee: {withdrawal['fee']}")
        else:
            print(f"Error: {data['ret_msg']}")
    else:
        print(f"Error: {response.status_code}")

get_withdrawal_fee()