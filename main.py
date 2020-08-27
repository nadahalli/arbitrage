import requests
import json
import time

URL = "http://bitcoin:BfVSZsyf8UV34UEFxp8FCB2X@127.0.0.1:8332"

def pprint(x):
    print(json.dumps(x, indent=4, sort_keys=True))

def get_raw_transaction(txid):
    payload = {
        "method": "getrawtransaction",
        "params": [txid, True],
    }
    response = requests.post(URL, json=payload).json()

    return(response["result"])

def get_num_transactions(block):
    return len(block["transactions"])

def get_best_blockhash():
    payload = {
        "method": "getbestblockhash",
        "params": [],
    }
    response = requests.post(URL, json=payload).json()

    return(response["result"])

def get_block_txids(blockhash):
    payload = {
        "method": "getblock",
        "params": [blockhash],
    }
    response = requests.post(URL, json=payload).json()

    return(response["result"]['tx'])

def get_bitcoin_price():
    COINDESK_API = "https://api.coindesk.com/v1/bpi/currentprice.json"
    response = requests.get(COINDESK_API)
    return response.json()['bpi']['USD']['rate_float']

if __name__ == "__main__":
    old_tip = ""
    while True:
        tip = get_best_blockhash()
        if tip == old_tip:
            time.sleep(1)
            continue
        old_tip = tip
        block_input = 0
        block_output = 0
        block_fees = 0
        number_of_transactions = 0
        for txid in get_block_txids(tip):
            number_of_transactions += 1
            is_coinbase = False
            txn = get_raw_transaction(txid)
            total_input = 0
            for itxn in txn['vin']:
                if 'coinbase' in itxn:
                    is_coinbase = True
                    break
                index = itxn['vout']
                itxn_full = get_raw_transaction(itxn['txid'])
                for ioutput in itxn_full['vout']:
                    if ioutput['n'] == index:
                        total_input += ioutput['value']
            block_input += total_input

            total_output = 0
            for output in txn['vout']:
                total_output += output['value']

            fees = 0
            if is_coinbase:
                block_reward = total_output
                is_coinbase = False
            else:
                fees = total_input - total_output
            block_output += total_output
            block_fees += fees
        bitcoin_price = get_bitcoin_price()
        print('Blockhash                 = ', tip)
        print('Total Inputs in BTC       = ', block_input)
        print('Total Outputs in BTC      = ', block_output)
        print('Total Fees in BTC         = ', block_fees)
        print('Total Miner Reward in BTC = ', block_reward)
        print('Total Transactions        = ', number_of_transactions)
        print('Total Outputs in USD      = ', block_output * bitcoin_price)
        print('-' * 10)

        

