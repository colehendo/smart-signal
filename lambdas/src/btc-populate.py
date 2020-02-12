import json
import time
import datetime
from decimal import Decimal
import requests

import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb')

def populate(event, context):
    table = dynamodb.Table('BTC_second_free')
    i = 0

    while i < 60:
        if ((time.time() % 1) == 0):
            timestamp = int(time.time())
            btc = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
            price = Decimal(btc.json()["data"]["amount"])

            minute(timestamp, price)
            fifteen_minute(timestamp, price)
            hour(timestamp, price)
            four_hour(timestamp, price)
            day(timestamp, price)
            week(timestamp, price)
            month(timestamp, price)

            item = {
                's': 'BTC',
                't': timestamp + 60,
                'p': price
            }

            table.put_item(Item = item)
            
            print(time.time())
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

def minute(timestamp, price):
    table = dynamodb.Table('BTC_minute_free')

    if ((timestamp % 60) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        volume = Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))
        end_of_period('BTC_minute_free', timestamp, price, 86400, 60, volume)

    else:
        update('BTC_minute_free', timestamp, price, 86400, 60)

def fifteen_minute(timestamp, price):
    table = dynamodb.Table('BTC_fifteen_minute_free')     

    if ((timestamp % 900) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=15&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        data = volume_api.json()["Data"]["Data"]
        volume = 0
        for i in range(0, 15):
            volume += data[i]["volumeto"]
        end_of_period('BTC_fifteen_minute_free', timestamp, price, 604800, 900, Decimal(str(volume)))

    else:
        update('BTC_fifteen_minute_free', timestamp, price, 604800, 900)

def hour(timestamp, price):
    table = dynamodb.Table('BTC_hour_free')     

    if ((timestamp % 3600) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        volume = Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))
        end_of_period('BTC_hour_free', timestamp, price, 2628000, 3600, volume)

    else:
        update('BTC_hour_free', timestamp, price, 2628000, 3600)

def four_hour(timestamp, price):
    table = dynamodb.Table('BTC_four_hour_free')     

    if ((timestamp % 14400) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=4&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        data = volume_api.json()["Data"]["Data"]
        volume = 0
        for i in range(0, 4):
            volume += data[i]["volumeto"]
        end_of_period('BTC_four_hour_free', timestamp, price, 15768000, 14400, Decimal(str(volume)))

    else:
        update('BTC_four_hour_free', timestamp, price, 15768000, 14400)

def day(timestamp, price):
    table = dynamodb.Table('BTC_day_free')     

    if ((timestamp % 86400) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        volume = Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))
        end_of_period('BTC_day_free', timestamp, price, 157680000, 86400, volume)

    else:
        update('BTC_day_free', timestamp, price, 157680000, 86400)

def week(timestamp, price):
    table = dynamodb.Table('BTC_week_free')     

    if ((timestamp % 604800) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=7&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        data = volume_api.json()["Data"]["Data"]
        volume = 0
        for i in range(0, 7):
            volume += data[i]["volumeto"]
        end_of_period('BTC_week_free', timestamp, price, 0, 604800, Decimal(str(volume)))

    else:
        update('BTC_week_free', timestamp, price, 0, 604800)

def month(timestamp, price):
    table = dynamodb.Table('BTC_month_free')     

    if ((timestamp % 2628000) == 0):
        volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=730&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
        data = volume_api.json()["Data"]["Data"]
        volume = 0
        for i in range(0, 730):
            volume += data[i]["volumeto"]
        end_of_period('BTC_month_free', timestamp, price, 0, 2628000, Decimal(str(volume)))

    else:
        update('BTC_month_free', timestamp, price, 0, 2628000)

def end_of_period(table, timestamp, price, ttl_increase, difference, volume):
    table = dynamodb.Table(table)

    item = {
        's': 'BTC',
        't': timestamp + ttl_increase,
        'h': price,
        'l': price,
        'o': price,
        'c': price,
    }

    table.put_item(Item = item)

    try:
        result = table.get_item(
            Key = {
                's': 'BTC',
                't': ((timestamp + ttl_increase) - difference)
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Item' in result:
            expressionAttributeValues = {
                ':x': 0,
                ':v': volume
            }
            if ((result['Item']['c'] - result['Item']['o']) != 0):
                expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

            update_result = table.update_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + ttl_increase) - difference)
                },
                UpdateExpression = "set x = :x, v = :v",
                ExpressionAttributeValues = expressionAttributeValues,
                ReturnValues="UPDATED_NEW"
            )

def update(table, timestamp, price, ttl_increase, difference):
    table = dynamodb.Table(table)

    try:
        result = table.get_item(
            Key = {
                's': 'BTC',
                't': ((timestamp + ttl_increase) - (timestamp % difference))
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Item' in result:
            key = {
                's': 'BTC',
                't': ((timestamp + ttl_increase) - (timestamp % difference))
            }
            updateExpression = "set c = :c"
            expressionAttributeValues = {
                ':c': price
            }

            if (result['Item']['h'] < price):
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues.update({':h': price})

            if (result['Item']['l'] > price):
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues.update({':l': price})

            if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                updateExpression = "set c = :c, h = :h, l = :l"

            update_result = table.update_item(
                Key = key,
                UpdateExpression = updateExpression,
                ExpressionAttributeValues = expressionAttributeValues,
                ReturnValues = "UPDATED_NEW"
            )