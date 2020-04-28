# Main cryptocompare API key: 2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8
# Backup cryptocompare API key: 52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8

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
    # Increases the count by 1, breaks when index == 60
    index = event['iterator']['index'] + 1
    i = 0

    while i < 1:
        # If it is at the start of a second period, run everything
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())
            btc = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
            price = Decimal(btc.json()["data"]["amount"])

            item = {
                's': 'BTC',
                't': (timestamp + 600),
                'p': price
            }

            # Write the new price value into the seconds table
            try:
                table.put_item(Item = item)
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])

            minute(timestamp, price)
            fifteen_minute(timestamp, price)
            hour(timestamp, price)
            four_hour(timestamp, price)
            day(timestamp, price)
            week(timestamp, price)
            month(timestamp, price)

            i += 1

    return {
        'index': index
    }

def minute(timestamp, price):
    table = dynamodb.Table('BTC_minute')

    # If it is at the start of a new minute, calculate the volume
    # of the past minute period, write that volume in along with the
    # change, write a new row to the minute table
    if ((timestamp % 60) == 0):
        volume = calculate_volume('single', 0, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_minute', timestamp, price, 86400, 60, volume)

    # If it's not starting a new minute, update the latest value in the table
    else:
        update('BTC_minute', timestamp, price, 86400, 60, 'single', 0, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def fifteen_minute(timestamp, price):
    table = dynamodb.Table('BTC_fifteen_minute')     

    # If it is at the start of a new fifteen minute period, calculate
    # the volume of the past period, write that volume in along with the
    # change, write a new row to the fifteen minute table
    if ((timestamp % 900) == 0):
        volume = calculate_volume('range', 15, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=15&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_fifteen_minute', timestamp, price, 604800, 900, volume)

    # If it's not starting a new fifteen minute period,
    # update the latest value in the table
    else:
        update('BTC_fifteen_minute', timestamp, price, 604800, 900, 'range', 15, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=15&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def hour(timestamp, price):
    table = dynamodb.Table('BTC_hour')

    # If it is at the start of a new hour, calculate the volume of
    # the past hour, write that volume in along with the
    # change, write a new row to the hour table
    if ((timestamp % 3600) == 0):
        volume = calculate_volume('single', 0, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_hour', timestamp, price, 2628000, 3600, volume)

    # If it's not starting a new hour,
    # update the latest value in the table
    else:
        update('BTC_hour', timestamp, price, 2628000, 3600, 'single', 0, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def four_hour(timestamp, price):
    table = dynamodb.Table('BTC_four_hour')     

    # If it is at the start of a new four hour period,
    # calculate the volume of the past period, write that volume in
    # along with the change, write a new row to the four hour table
    if ((timestamp % 14400) == 0):
        volume = calculate_volume('range', 4, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=4&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_four_hour', timestamp, price, 15768000, 14400, volume)

    # If it's not starting a new four hour period,
    # update the latest value in the table
    else:
        update('BTC_four_hour', timestamp, price, 15768000, 14400, 'range', 4, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=4&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def day(timestamp, price):
    table = dynamodb.Table('BTC_day')     

    if ((timestamp % 86400) == 0):
        volume = calculate_volume('single', 0, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_day', timestamp, price, 157680000, 86400, volume)

    else:
        update('BTC_day', timestamp, price, 157680000, 86400, 'single', 0, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def week(timestamp, price):
    table = dynamodb.Table('BTC_week')     

    if ((timestamp % 604800) == 0):
        volume = calculate_volume('range', 7, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=7&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_week', timestamp, price, 0, 604800, volume)

    else:
        update('BTC_week', timestamp, price, 0, 604800, 'range', 7, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=7&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def month(timestamp, price):
    table = dynamodb.Table('BTC_month')
    today = datetime.date.today()
    this_month = int(time.mktime((today.year, today.month, 1, 0, 0, 0, 0, 0, 0)))
    if (today.month == 1):
        difference = (this_month - int(time.mktime(((today.year - 1), 12, 1, 0, 0, 0, 0, 0, 0))))
    else:
        difference = (this_month - int(time.mktime((today.year, (today.month - 1), 1, 0, 0, 0, 0, 0, 0))))

    if (timestamp == this_month):
        volume = calculate_volume('range', 730, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=730&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        end_of_period('BTC_month', timestamp, price, 0, difference, volume)

    else:
        update('BTC_month', this_month, price, 0, difference, 'range', 730, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=730&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

def end_of_period(table, timestamp, price, ttl_increase, difference, volume):
    table = dynamodb.Table(table)

    item = {
        's': 'BTC',
        't': (timestamp + ttl_increase),
        'h': price,
        'l': price,
        'o': price,
        'c': price,
    }

    try:
        table.put_item(Item = item)
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])

    try:
        result = table.get_item(
            Key = {
                's': 'BTC',
                't': ((timestamp + ttl_increase) - difference)
            }
        )
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Item' in result:
            expressionAttributeValues = {
                ':x': 0,
                ':v': volume
            }
            if ((result['Item']['c'] - result['Item']['o']) != 0):
                expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

            try:
                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': ((timestamp + ttl_increase) - difference)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])

def update(table_str, timestamp, price, ttl_increase, difference, api_type, range_end, api_endpoint):
    table = dynamodb.Table(table_str)

    if (table_str == 'BTC_month'):
        update_time = timestamp
    else:
        update_time = ((timestamp + ttl_increase) - (timestamp % difference))

    try:
        result = table.get_item(
            Key = {
                's': 'BTC',
                't': update_time
            }
        )
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Item' in result:
            key = {
                's': 'BTC',
                't': update_time
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

            try:
                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])

        else:
            volume = calculate_volume(api_type, range_end, api_endpoint)
            if (table_str == 'BTC_month'):
                end_of_period(table_str, timestamp, price, 0, difference, volume)
            else:
                end_of_period(table_str, timestamp, price, (ttl_increase - (timestamp % difference)), difference, volume)

def calculate_volume(api_type, range_end, api_endpoint):
    if api_type == 'range':
        volume_api = requests.get(api_endpoint)
        data = volume_api.json()["Data"]["Data"]
        volume = 0
        for i in range(0, range_end):
            volume += data[i]["volumeto"]
        return Decimal(str(volume))

    else:
        volume_api = requests.get(api_endpoint)
        return Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))