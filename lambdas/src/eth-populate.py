import json
import time
import datetime
from decimal import Decimal
import requests

import boto3
dynamodb = boto3.resource('dynamodb')

def populate(event, context):

    table = dynamodb.Table('another_test')
    i = 0

    while i < 60:
        if ((time.time() % 1) == 0):
            timestamp = int(time.time()) + 60
            eth = requests.get('https://api.coinbase.com/v2/prices/ETH-USD/spot')
            price = Decimal(eth.json()["data"]["amount"])

            item = {
                's': 'ETH',
                't': timestamp,
                'p': price,
            }

            table.put_item(Item=item)

            i += 1

    body = {
        "message": "Table updated successfully",
        "item": item
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """