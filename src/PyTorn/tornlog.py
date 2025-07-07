#! /usr/bin/env python3
'''Read Torn Logs'''

# /1.0/ Import Dependencies
import os
import json
import requests
import time
import datetime

# /2.0/ Global Variables
_dir = os.path.dirname(os.path.abspath(__file__))
key = ""
api_url = ""
curl = f"curl -X 'GET' 'https://api.torn.com/v2/user?selections=log' -H 'accept: application/json' -H 'Authorization: ApiKey {key}'"

# /3.0/ User Data Functions
def getkey () :
    '''Get the API key from user.json'''
    global key, api_url
    patx = os.path.join(_dir, "data", "user.json")
    with open (patx, 'r', encoding='utf-8') as f :
        xxf = json.load(f)
        key = xxf['My_Data']['key']
        api_url = f"https://api.torn.com/user/?selections=log&key={key}&comment=LogPuller"
    return key

# /4.0/ Main Functions
def gather () :
    '''Gather data from the API'''
    global key
    key = getkey()
    if not key :
        print("[ERROR] No API key found. Please set your API key in user.json.")
        return None
    else:
        result = {
            "pm": {
                "buys": {
                    "total": 0,
                    "volume": 0,
                    "record": {}
                },
                "sells": {
                    "total": 0,
                    "volume": 0,
                    "record": {}
                },
                "P&L": {}
            },
            "im": {}
        },
        item_gained = []
        item_lost = []
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                raw = response.json()
                if 'error' in raw:
                    print(f"[ERROR] API returned error: {raw['error']}")
                    return None
                logs = list(raw['log'].keys())
                for event in logs:
                    data = raw['log'][event]
                    title = data['title'].lower()
                    if title in ['item found', 'item received', 'item sent (to you)', 'item transfer (to you)']:
                        for item in data['data'].get('items', []):
                            item_id = str(item['id'])
                            item_gained.add((item_id, event))
                    elif title in ['item used', 'item trashed', 'item sent', 'item transfer']:
                        for item in data['data'].get('items', []):
                            item_id = str(item['id'])
                            item_lost.add((item_id, event))
                for event in logs:
                    data = raw['log'][event]
                    title = data['title'].lower()

            # /4.1/ Points Market Sell
                    if title == 'points market sell':
                        qty = data['data']['quantity']
                        price = data['data']['cost_each']
                        total = data['data']['cost_total']
                        result['pm']['sells']['total'] += total
                        result['pm']['sells']['volume'] += qty
                        price_str = str(price)
                        if price_str not in result['pm']['sells']['record']:
                            result['pm']['sells']['record'][price_str] = 0
                        result['pm']['sells']['record'][price_str] += qty

            # /4.2/ Points Market Buy
                    elif title == 'points market buy':
                        qty = data['data']['quantity']
                        price = data['data']['cost_each']
                        total = data['data']['cost_total']
                        result['pm']['buys']['total'] += total
                        result['pm']['buys']['volume'] += qty
                        price_str = str(price)
                        if price_str not in result['pm']['buys']['record']:
                            result['pm']['buys']['record'][price_str] = 0
                        result['pm']['buys']['record'][price_str] += qty

            # /4.3/ Item Market Buy
                    elif title == 'item market buy':
                        for item in data['data']['items']:
                            item_id = str(item['id'])
                            qty = item['qty']
                            price = data['data']['cost_each']
                            total = data['data']['cost_total']
                            if item_id not in result['im']:
                                result['im'][item_id] = {
                                    "buys": {"total": 0, "volume": 0, "record": {}},
                                    "sells": {"total": 0, "volume": 0, "record": {}},
                                    "P&L": {}
                                }
                            result['im'][item_id]['buys']['total'] += total
                            result['im'][item_id]['buys']['volume'] += qty
                            price_str = str(price)
                            if price_str not in result['im'][item_id]['buys']['record']:
                                result['im'][item_id]['buys']['record'][price_str] = 0
                            result['im'][item_id]['buys']['record'][price_str] += qty

            # /4.4/ Item Market Sell
                    elif title == 'item market sell':
                        for item in data['data']['items']:
                            item_id = str(item['id'])
                            qty = item['qty']
                            price = data['data']['cost_each']
                            total = data['data']['cost_total']
                            if item_id not in result['im']:
                                result['im'][item_id] = {
                                    "buys": {"total": 0, "volume": 0, "record": {}},
                                    "sells": {"total": 0, "volume": 0, "record": {}},
                                    "P&L": {}
                                }
                            result['im'][item_id]['sells']['total'] += total
                            result['im'][item_id]['sells']['volume'] += qty
                            price_str = str(price)
                            if price_str not in result['im'][item_id]['sells']['record']:
                                result['im'][item_id]['sells']['record'][price_str] = 0
                            result['im'][item_id]['sells']['record'][price_str] += qty

            # /4.5/ Calculate P&L's and averages
                pm_buys = result['pm']['buys']
                pm_sells = result['pm']['sells']
                pm_gain = pm_sells['total'] - pm_buys['total']
                pm_pl = (pm_gain) / pm_buys['total'] * 100 if pm_buys['total'] > 0 else 0
                pm_av = pm_sells['total'] / pm_sells['volume'] if pm_sells['volume'] > 0 else 0
                result['pm']['P&L'] = {"rate": pm_pl, "avg_price": pm_av, "gain": pm_gain}
                for item_id in result['im']:
                    buys = result['im'][item_id]['buys']
                    sells = result['im'][item_id]['sells']
                    im_gain = sells['total'] - buys['total']
                    im_pl = (im_gain) / buys['total'] * 100 if buys['total'] > 0 else 0
                    im_av = sells['total'] / sells['volume'] if sells['volume'] > 0 else 0
                    result['im'][item_id]['P&L'] = {"rate": im_pl, "avg_price": im_av, "gain": im_gain}

            # /4.6/ Sort item ids numerically
                result['im'] = dict(sorted(result['im'].items(), key=lambda x: int(x[0])))
                id_item_path = os.path.join(_dir, "data", "ID_Item.json")
                with open(id_item_path, 'r', encoding='utf-8') as f:
                    id_item_map = json.load(f)
                im_named = {}
                for item_id, data in result['im'].items():
                    name = id_item_map.get(item_id, f"Unknown({item_id})")
                    im_named[name] = data

            # /4.7/ End the Functon and Error Handle
                result['im'] = im_named
                print(json.dumps(result, indent=4))
                input("Press Enter to Exit")
                return result
            else:
                print(f"[ERROR] Failed to fetch data. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return None

# /5.0/ Runnit
if __name__ == "__main__" :
    try:
        gather ()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        input("Press Enter to Exit")
