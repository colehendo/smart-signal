import json
import time
import datetime
import requests

import boto3
dynamodb = boto3.resource('dynamodb')

def populate(event, context):
    print("start")
    print(time.time())

    table = dynamodb.Table('test_second')
    i = 0

    while i < 600:
        if ((time.time() % 1) == 0):
            btc_current = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
            btc_price = btc_current.json()["data"]["amount"]
            timestamp = int(time.time())

            print(timestamp)
            print(btc_price)

            item = {
                's': 'BTC',
                't': timestamp,
                'p': btc_price,
            }

            # table.put_item(Item=item)

            # table.delete_item(
            #     Key={
            #         't': timestamp + 60
            #     }
            # )
            print(i)
            i += 1


    body = {
        "message": "Table updated successfully",
        "item": item
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    print("end")
    print(time.time())

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """