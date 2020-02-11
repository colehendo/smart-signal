import json
import time
import datetime
from decimal import Decimal
import requests

import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb')

def populate(event, context):

    table = dynamodb.Table('BTC_second')
    initial_prev_set = False
    prev_price = Decimal(0.0)
    i = 0

    while i < 60:
        if ((time.time() % 1) == 0):
            timestamp = int(time.time())
            btc = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
            price = Decimal(btc.json()["data"]["amount"])
            if (initial_prev_set == False):
                prev_price = price
                initial_prev_set = True

            if ((timestamp % 2) == 0):
                minute(timestamp, prev_price, price)

            else:
                prev_price = price

            item = {
                's': 'BTC',
                't': timestamp + 60,
                'p': price
            }

            table.put_item(Item=item)


            i += 1

    body = {
        "message": "Table updated successfully",
        "item": item
    }

    response = {
        "statusCode": 200,
        "body": body
    }

    return response

def minute(timestamp, first_price, second_price):
    table = dynamodb.Table('BTC_minute')

    if ((timestamp % 60) == 0):
        # call api and write to previous
        item = {
            's': 'BTC',
            't': timestamp + 86400,
            'h': second_price,
            'l': second_price,
            'o': second_price,
            'c': second_price,
        }

        table.put_item(Item=item)

    else:
        try:
            result = table.get_item(
                Key={
                    's': 'BTC',
                    't': ((timestamp + 86400) - (timestamp % 60))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:

            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': ((timestamp + 86400) - (timestamp % 60))
                }
                updateExpression = "set c=:c"
                expressionAttributeValues = {
                    ':c': second_price
                }

                # if there is a new high
                if ((result['Item']['h'] < first_price) or (result['Item']['h'] < second_price)):
                    updateExpression = "set c=:c, h=:h"
                    if (first_price > second_price):
                        expressionAttributeValues.update({':h': first_price})
                    else:
                        expressionAttributeValues.update({':h': second_price})

                # if there is just a new low
                if ((result['Item']['l'] > first_price) or (result['Item']['l'] > second_price)):
                    updateExpression = "set c=:c, l=:l"
                    if (first_price < second_price):
                        expressionAttributeValues.update({':l': first_price})
                    else:
                        expressionAttributeValues.update({':l': second_price})

                if (((result['Item']['h'] < first_price) or (result['Item']['h'] < second_price)) and ((result['Item']['l'] > first_price) or (result['Item']['l'] > second_price))):
                    updateExpression = "set c=:c, h=:h, l=:l"

                update_result = table.update_item(
                    Key=key,
                    UpdateExpression=updateExpression,
                    ExpressionAttributeValues=expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )