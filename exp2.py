import requests
import time
import hashlib
import hmac
import uuid


api_key='V1IkiWjudAPBY7xsdc'
secret_key='fLPtrlAkhENn9PXhjR0cw1wHeqanRBG90iiE'
httpClient=requests.Session()
recv_window=str(5000)
url="https://api.bybit.com" # Testnet endpoint


def HTTP_Request(endPoint,method,payload,Info):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genSignature(payload)
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method=="POST"):
        response = httpClient.request(method, url+endPoint, headers=headers, data=payload)
    else:
        response = httpClient.request(method, url+endPoint+"?"+payload, headers=headers)
    return response.json()


def genSignature(payload):
    param_str= str(time_stamp) + api_key + recv_window + payload
    hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
    signature = hash.hexdigest()
    return signature


endpoint="/v5/asset/coin/query-info"
method="GET"
params="coin=DOGE"
result = HTTP_Request(endpoint,method,params,"List")

print(result)

for i in result['result']['rows'][0]['chains']:
    print(i)
