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
    table = dynamodb.Table('BTC_test_second')

    current_time = int(time.time())
    # 840 seconds in 14 min period
    end_time = current_time + 840
    last_recorded = current_time - 1
    
    total_missing_records = 0

    while current_time < end_time:
        current_time = int(time.time())
        # If it is at the start of a second period, run everything
        if ((time.time() % 1) < 0.1):
            if last_recorded != current_time - 1:
                print(f'missing {current_time - last_recorded + 1} records')
                total_missing_records += (current_time - last_recorded + 1)
            last_recorded = current_time
            btc = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
            price = Decimal(btc.json()["data"]["amount"])

            item = {
                's': 'BTC',
                't': current_time,
                'p': price
            }

            # Write the new price value into the seconds table
            try:
                table.put_item(Item = item)
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])

            minute(current_time, price)
            fifteen_minute(current_time, price)
            hour(current_time, price)
            four_hour(current_time, price)
            day(current_time, price)
            week(current_time, price)

    print(f'TOTAL MISSING RECORDS: {total_missing_records}')
    return

minute_close = 0
minute_high = 0
minute_low = 0


def minute(timestamp, price):
    global minute_close, minute_high, minute_low
    table = dynamodb.Table('BTC_minute')

    # If it is at the start of a new minute, calculate the volume
    # of the past minute period, write that volume in along with the
    # change, write a new row to the minute table
    if ((timestamp % 60) == 0):
        minute_close = minute_high = minute_low = price
        print(f'new minute candle. close: {minute_close}, high: {minute_high}, low: {minute_low}')
        # volume = calculate_volume('single', 0, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        # end_of_period('BTC_minute', timestamp, price, 86400, 60, volume)

    # If it's not starting a new minute, update the latest value in the table
    else:
        if price != minute_close:
            minute_close = price
            if price > minute_high:
                minute_high = price
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues = {
                    ':c': price,
                    ':h': price
                }
            elif price < minute_low:
                minute_low = price
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues = {
                    ':c': price,
                    ':l': price
                }
            else:
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }
            print(f'updating minute with {expressionAttributeValues}')
            # update('BTC_minute', timestamp, price, 86400, 60, 'single', 0, updateExpression, expressionAttributeValues, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

fifteen_minute_close = 0
fifteen_minute_high = 0
fifteen_minute_low = 0


def fifteen_minute(timestamp, price):
    global fifteen_minute_close, fifteen_minute_high, fifteen_minute_low
    table = dynamodb.Table('BTC_fifteen_minute')

    # If it is at the start of a new fifteen minute period, calculate
    # the volume of the past period, write that volume in along with the
    # change, write a new row to the fifteen minute table
    if ((timestamp % 900) == 0):
        fifteen_minute_close = fifteen_minute_high = fifteen_minute_low = price
        print(f'new fifteen_minute candle. close: {fifteen_minute_close}, high: {fifteen_minute_high}, low: {fifteen_minute_low}')
        # volume = calculate_volume('range', 15, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=15&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        # end_of_period('BTC_fifteen_minute', timestamp, price, 604800, 900, volume)

    # If it's not starting a new fifteen minute period,
    # update the latest value in the table
    else:
        if price != fifteen_minute_close:
            fifteen_minute_close = price
            if price > fifteen_minute_high:
                fifteen_minute_high = price
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues = {
                    ':c': price,
                    ':h': price
                }
            elif price < fifteen_minute_low:
                fifteen_minute_low = price
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues = {
                    ':c': price,
                    ':l': price
                }
            else:
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }
            print(f'updating fifteen minute with {expressionAttributeValues}')
            # update('BTC_fifteen_minute', timestamp, price, 604800, 900, 'range', 15, updateExpression, expressionAttributeValues, 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=15&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

hour_close = 0
hour_high = 0
hour_low = 0


def hour(timestamp, price):
    global hour_close, hour_high, hour_low
    table = dynamodb.Table('BTC_hour')

    # If it is at the start of a new hour, calculate the volume of
    # the past hour, write that volume in along with the
    # change, write a new row to the hour table
    if ((timestamp % 3600) == 0):
        hour_close = hour_high = hour_low = price
        print(f'new hour candle. close: {hour_close}, high: {hour_high}, low: {hour_low}')
        # volume = calculate_volume('single', 0, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        # end_of_period('BTC_hour', timestamp, price, 2628000, 3600, volume)

    # If it's not starting a new hour,
    # update the latest value in the table
    else:
        if price != hour_close:
            hour_close = price
            if price > hour_high:
                hour_high = price
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues = {
                    ':c': price,
                    ':h': price
                }
            elif price < hour_low:
                hour_low = price
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues = {
                    ':c': price,
                    ':l': price
                }
            else:
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }
            print(f'updating hour with {expressionAttributeValues}')
            # update('BTC_hour', timestamp, price, 2628000, 3600, 'single', 0, updateExpression, expressionAttributeValues, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

four_hour_close = 0
four_hour_high = 0
four_hour_low = 0


def four_hour(timestamp, price):
    global four_hour_close, four_hour_high, four_hour_low
    table = dynamodb.Table('BTC_four_hour')

    # If it is at the start of a new four hour period,
    # calculate the volume of the past period, write that volume in
    # along with the change, write a new row to the four hour table
    if ((timestamp % 14400) == 0):
        four_hour_close = four_hour_high = four_hour_low = price
        print(f'new four hour candle. close: {four_hour_close}, high: {four_hour_high}, low: {four_hour_low}')
        # volume = calculate_volume('range', 4, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=4&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        # end_of_period('BTC_four_hour', timestamp, price, 15768000, 14400, volume)

    # If it's not starting a new four hour period,
    # update the latest value in the table
    else:
        if price != four_hour_close:
            four_hour_close = price
            if price > four_hour_high:
                four_hour_high = price
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues = {
                    ':c': price,
                    ':h': price
                }
            elif price < four_hour_low:
                four_hour_low = price
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues = {
                    ':c': price,
                    ':l': price
                }
            else:
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }
            print(f'updating four_hour with {expressionAttributeValues}')
            # update('BTC_four_hour', timestamp, price, 15768000, 14400, 'range', 4, updateExpression, expressionAttributeValues, 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=4&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

day_close = 0
day_high = 0
day_low = 0


def day(timestamp, price):
    global day_close, day_high, day_low
    table = dynamodb.Table('BTC_day')

    if ((timestamp % 86400) == 0):
        day_close = day_high = day_low = price
        print(f'new day candle. close: {day_close}, high: {day_high}, low: {day_low}')
        # volume = calculate_volume('single', 0, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        # end_of_period('BTC_day', timestamp, price, 157680000, 86400, volume)

    else:
        if price != day_close:
            day_close = price
            if price > day_high:
                day_high = price
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues = {
                    ':c': price,
                    ':h': price
                }
            elif price < day_low:
                day_low = price
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues = {
                    ':c': price,
                    ':l': price
                }
            else:
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }
            print(f'updating day with {expressionAttributeValues}')
            # update('BTC_day', timestamp, price, 157680000, 86400, 'single', 0, updateExpression, expressionAttributeValues, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')

week_close = 0
week_high = 0
week_low = 0


def week(timestamp, price):
    global week_close, week_high, week_low
    table = dynamodb.Table('BTC_week')

    if ((timestamp % 604800) == 0):
        week_close = week_high = week_low = price
        print(f'new week candle. close: {week_close}, high: {week_high}, low: {week_low}')
        # volume = calculate_volume('range', 7, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=7&e=coinbase&api_key=2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8')
        # end_of_period('BTC_week', timestamp, price, 0, 604800, volume)

    else:
        if price != week_close:
            week_close = price
            if price > week_high:
                week_high = price
                updateExpression = "set c = :c, h = :h"
                expressionAttributeValues = {
                    ':c': price,
                    ':h': price
                }
            elif price < week_low:
                week_low = price
                updateExpression = "set c = :c, l = :l"
                expressionAttributeValues = {
                    ':c': price,
                    ':l': price
                }
            else:
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }
            print(f'updating week with {expressionAttributeValues}')
            # update('BTC_week', timestamp, price, 0, 604800, 'range', 7, updateExpression, expressionAttributeValues, 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=7&e=coinbase&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')



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


def update(table_str, timestamp, price, ttl_increase, difference, api_type, range_end, update_expression, expressionAttributeValues, api_endpoint):
    table = dynamodb.Table(table_str)

    update_time = ((timestamp + ttl_increase) - (timestamp % difference))

    key = {
        's': 'BTC',
        't': update_time
    }

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