import hmac
import time
import hashlib
import requests
import json
import pandas as pd

apiKey = ""
apiSecret = ""

def auth(uri, method, payload, apiKey, apiSecret):
    timestamp = str(round(time.time()*1000))
    contentHash = hashlib.sha512(payload).hexdigest()
    
    array = [timestamp, uri, method, contentHash]
    s= ''
    preSign = s.join(str(v) for v in array)
    signature = hmac.new(apiSecret.encode() ,preSign.encode(), hashlib.sha512).hexdigest()

    headers = {
     'Accept':'application/json',
     'Api-Key':apiKey,
     'Api-Timestamp':timestamp,
     'Api-Content-Hash':contentHash,
     'Api-Signature':signature,
     'Content-Type':'application/json'
    }
    
    return headers

while True:
    try:
        ticker = requests.get('https://api.bittrex.com/v3/markets/BTC-USD/ticker').json()
    except Exception as e:
        print(f'Unable to obtain ticker data: {e}')
    
    if float(ticker['bidRate']) >= 50000:

        uri = 'https://api.bittrex.com/v3/orders'

        content = { "marketSymbol":"USDC-ETH",
         "direction":"SELL",
         "type":"LIMIT",
         "limit":"0.0005",
         "quantity":"20",
         "timeInForce":"GOOD_TIL_CANCELLED"
        }

        payload = bytes(json.dumps(content),'utf-8')
        
        try:
            data = requests.post(uri, 
                                 data=payload, 
                                 headers = auth(uri, 'POST', payload, apiKey, apiSecret),
                                 timeout=10
                                ).json()
            print(data)
        except Exception as e:
            print(f'Unable to place order: {e}')
        
        time.sleep(2)
        
        try:
            payload = ""
            uri = f'https://api.bittrex.com/v3/orders/{data["id"]}'

            check = requests.get(uri, 
                                 data=payload, 
                                 headers=auth(uri, 'GET', payload.encode(), apiKey, apiSecret), 
                                 timeout=10
                                ).json()
            print(check)
        except Exception as e:
            print(f'Unable to check order: {e}')
        
        if check == 'OPEN':
            print ('Order placed at {}'.format(pd.Timestamp.now()))
            break
        else:
            print ('Order closed at {}'.format(pd.Timestamp.now()))
            break
    else:
        time.sleep(60)
        continue
