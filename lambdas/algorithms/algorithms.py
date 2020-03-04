# Main cryptocompare API key: 52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8
# Backup cryptocompare API key: 2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8

import time
from decimal import Decimal
import simplejson as json
import pandas as pd
import ta

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

def calculate(event, context):
    # index = event['iterator']['index'] + 1
    i = 0

    hour_ttl = 2628000
    hour_gap = 3600

    four_hour_ttl = 15768000
    four_hour_gap = 14400

    day_ttl = 157680000
    day_gap = 86400

    week_ttl = 0
    week_gap = 604800

    while i < 1:
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())

            # Get the different rsi and macd values based on
            # the last 30 values from each table
            get_values('BTC_hour', timestamp, hour_ttl, hour_gap, 30)
            get_values('BTC_four_hour', timestamp, four_hour_ttl, four_hour_gap, 30)
            get_values('BTC_day', timestamp, day_ttl, day_gap, 30)
            get_values('BTC_week', timestamp, week_ttl, week_gap, 30)

            i += 1

    return {
        # 'index': index
    }

def get_values(table, timestamp, ttl, gap, timeframe):
    dynamo_table = dynamodb.Table(table)
    try:
        # Query the table for the last `timeframe` rows of data.
        # TTL and gap values can easily be found in btc-populate.py
        results = dynamo_table.query(
            KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + ttl) - (gap * timeframe))
        )
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in results:
            # Turn the returned object into a JSON string,
            # and pass it to pandas to make it readable for TA
            df = pd.read_json(json.dumps(results['Items']))

            # Get the past `timeframe` rsi values in a dataframe
            rsi_total = ta.momentum.rsi(close = df["c"], n = 14, fillna = True)
            for i in range(0, timeframe):
                if (rsi_total.iloc[i] < 100) and (rsi_total.iloc[i] > 0):
                    # Find the first value in the list that
                    # isn't equal to 100 or 0
                    rsi_val = rsi_total.iloc[i]
                    break

            # Get the past `timeframe` MACD histogram values in a dataframe
            macd_diff = ta.trend.macd_diff(close = df["c"], n_fast = 12, n_slow = 26, n_sign = 9, fillna = True)
            # The very first one is always 0. Comparing these two
            # next values allows us to see a reversal in trend
            macd_diff_new = macd_diff.iloc[1]
            macd_diff_prev = macd_diff.iloc[2]

            if (table == 'BTC_hour'):
                rsi(timestamp, 'rsi_hour', rsi_val, 20, 80, 30)
                rsi_macd(timestamp, 'rsi_macd_hour', rsi_val, 20, 80, macd_diff_new, macd_diff_prev)
            elif (table == 'BTC_four_hour'):
                rsi(timestamp, 'rsi_four_hour', rsi_val, 20, 80, 20)
                rsi_macd(timestamp, 'rsi_macd_four_hour', rsi_val, 20, 80, macd_diff_new, macd_diff_prev)
            elif (table == 'BTC_day'):
                rsi(timestamp, 'rsi_day', rsi_val, 30, 70, 10)
                rsi_macd(timestamp, 'rsi_macd_day', rsi_val, 30, 70, macd_diff_new, macd_diff_prev)
            elif (table == 'BTC_week'):
                rsi(timestamp, 'rsi_week', rsi_val, 40, 60, 0)
                rsi_macd(timestamp, 'rsi_macd_week', rsi_val, 40, 60, macd_diff_new, macd_diff_prev)
            else:
                return

def rsi(timestamp, bot, rsi, rsi_buy, rsi_sell, timeframe_adjust):
    ##Weekly = 0, Daily = 10, 4Hour = 20, Hour = 30..we will be subtracting these values from the strength to account for timeframe
    if (rsi < rsi_buy):
        strength = round(Decimal((100 - rsi - timeframe_adjust) / 100), 10)
        check_signal(timestamp, 'buy', strength, 'rsi', bot)
        check_signal(timestamp, 'buy', strength, 'rsi', 'rsi_all')
        print('BUY because our RSI is: ', rsi, ' bc of the indicator: ', bot)
    elif (rsi > rsi_sell):
        strength = round(Decimal((rsi - timeframe_adjust) / 100), 10)
        check_signal(timestamp, 'sell', strength, 'rsi', bot)
        check_signal(timestamp, 'sell', strength, 'rsi', 'rsi_all')
        print('Sell because our RSI is: ', rsi, ' bc of the indicator: ', bot)
    else:
        return


def rsi_macd(timestamp, bot, rsi, rsi_buy, rsi_sell, macd_diff_new, macd_diff_prev):
    if (rsi < rsi_buy):
        # Going from negative to positive indicates bullish trend. Buy
        if (macd_diff_new >= 0) and (macd_diff_prev < 0):
            strength = round(Decimal(((macd_diff_new - macd_diff_prev) / (100 - rsi))), 10)
            check_signal(timestamp, 'buy', strength, 'rsi_macd', bot)
            check_signal(timestamp, 'buy', strength, 'rsi_macd', 'rsi_macd_all')
            print('BUY BUY BUY: ', bot)
            print('rsi: ', rsi)
            print('macd new: ', macd_diff_new, ' macd prev: ', macd_diff_prev)
        else:
            return

    elif (rsi > rsi_sell):
        # Going from positive to negative indicates bearish trend. Sell
        if (macd_diff_new <= 0) and (macd_diff_prev > 0):
            strength = round(Decimal((abs(macd_diff_new - macd_diff_prev) / rsi)), 10)
            check_signal(timestamp, 'sell', strength, 'rsi_macd', bot)
            check_signal(timestamp, 'sell', strength, 'rsi_macd', 'rsi_macd_all')
            print('SELL SELL SELL: ', bot)
            print('rsi: ', rsi)
            print('macd new: ', macd_diff_new, ' macd prev: ', macd_diff_prev)
        else:
            return

    else:
        return

def check_signal(timestamp, signal, strength, indicator, bot):
    table = dynamodb.Table('BTC_signals')
    try:
        # Query for the signals on a specific timeframe and a specific indicator
        signals_result = table.query(
            KeyConditionExpression = Key('i').eq(bot) & Key('ts').gt(0)
        )
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        # If this is the first signal on the specific timeframe and indicator
        # or if this signal is different from the most recent signal
        if ('Items' not in signals_result) or (signals_result['Count'] == 0):
            if (signal == 'buy'):
                write_signal(timestamp, signal, strength, indicator, bot, 0)
            else:
                return
        # Checks if our most recent signal sent is equal to our current one
        # to avoid repetitive signals
        elif (signals_result['Items'][len(signals_result['Items']) - 1]['si'] != signal):
            write_signal(timestamp, signal, strength, indicator, bot, signals_result['Items'][len(signals_result['Items']) - 1]['st'])

        else:
            return

def write_signal(timestamp, signal, strength, indicator, bot, original_strength):
    table = dynamodb.Table('BTC_second')
    try:
        # Query for the last 10 seconds of prices, just to be safe
        second_result = table.query(
            KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + 60) - 10)
        )
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in second_result:
            latest_price = second_result['Items'][len(second_result['Items']) - 1]['p']
            item = {
                'ts': timestamp,
                'si': signal,
                'st': strength,
                'i': bot,
                'p': latest_price
            }

            try:
                # Write in the latest signal
                table = dynamodb.Table('BTC_signals')
                table.put_item(Item = item)
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])

            table = dynamodb.Table('BTC_bots')
            try:
                # Get the row for the bot associated with the timeframe and indicator
                bots_result = table.get_item(Key = {'name': bot})
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])
            else:
                if 'Item' in bots_result:
                    if (signal == 'sell'):
                        # The profit is the strength of the previous signal times the latest price.
                        # This keeps the amount sold proportional to the last buy signal,
                        # therefore emulating buying/selling a set amount of coins
                        transaction = round((original_strength * latest_price), 2)
                        total = round((bots_result['Item']['balance'] + transaction), 2)
                        rate = round((((total - 100000) / 100000) * 100), 4)
                        count = (bots_result['Item']['transactions'] + 1)
                        avg_rate = round((rate / count), 6)

                    else:
                        # The cost of the amount bought is the strength of the signal times the latest price
                        transaction = round((strength * latest_price), 2)
                        total = round((bots_result['Item']['balance'] - transaction), 2)
                        rate = round((((total - 100000) / 100000) * 100), 4)
                        count = (bots_result['Item']['transactions'] + 1)
                        avg_rate = round((rate / count), 6)

                    try:
                        # Update the associated bot with the latest values
                        update_result = table.update_item(
                            Key = {'name': bot},
                            UpdateExpression = "set balance = :b, total_roi = :tr, avg_roi = :ar, alg = :a, transaction_amt = :ta, prev_signal = :ps, transactions = :t",
                            ExpressionAttributeValues = {
                                ':b': total,
                                ':tr': rate,
                                ':ar': avg_rate,
                                ':a': indicator,
                                ':ta': transaction,
                                ':ps': signal,
                                ':t': count
                            },
                            ReturnValues="UPDATED_NEW"
                        )
                    except ClientError as e:
                        print(e.response['Error']['Code'])
                        print(e.response['ResponseMetadata']['HTTPStatusCode'])
                        print(e.response['Error']['Message'])
