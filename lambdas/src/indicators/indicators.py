import time
from decimal import Decimal
import simplejson as json
from itertools import combinations
from multiprocessing import Process, Pipe

import pandas as pd
import ta

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

#### SECTION FOR TESTING ALL COMBINATIONS ####

all_indicators = []
combo_results = []

month_candles = []
week_candles = []
day_candles = []
four_hour_candles = []
hour_candles = []
fifteen_minute_candles = []
minute_candles = []

month_ttl = 0
week_ttl = 0
day_ttl = 157680000
four_hour_ttl = 15768000
hour_ttl = 2628000
fifteen_minute_ttl = 604800
minute_ttl = 86400

def calculate(event, context):
    if (event['queryStringParameters'] == None):
        return {
            "statusCode": 502,
            "body": json.dumps("No parameters given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
    print(event['queryStringParameters'])

    # Load the payload into a usable format
    data = json.loads(event['queryStringParameters']['vals'])

    if not data:
        return {
            "statusCode": 502,
            "body": json.dumps("No data given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Remove the array of timeframes from the data
    timeframes = data[-1]
    del data[-1]

    if not data:
        return {
            "statusCode": 502,
            "body": "Data is in incorrect format",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    timeframe_data = []
    all_signals = []
    final_signals = []

    print('timeframes: ', timeframes)

    global month_candles
    global week_candles
    global day_candles
    global four_hour_candles
    global hour_candles
    global fifteen_minute_candles
    global minute_candles

    # Condense all signals of all indicators for each timeframe given
    # into a single array, and append that array to the main array
    if ('month' in timeframes): month_candles = get_data('BTC_month', month_ttl)
    if ('week' in timeframes): week_candles = get_data('BTC_week', week_ttl)
    if ('day' in timeframes): day_candles = get_data('BTC_day', day_ttl)
    if ('four_hour' in timeframes): four_hour_candles = get_data('BTC_four_hour', four_hour_ttl)
    if ('hour' in timeframes): hour_candles = get_data('BTC_hour', hour_ttl)
    if ('fifteen_minute' in timeframes): fifteen_minute_candles = get_data('BTC_fifteen_minute', fifteen_minute_ttl)
    if ('minute' in timeframes): minute_candles = get_data('BTC_minute', minute_ttl)

    for indicator in data:
        result = run_indicator(indicator)
        print('result: ', result)
        if result:
            timeframe_data.append(result[0])
            for data in result[1]:
                all_signals.append(data)


    if not all_signals:
        return {
            "statusCode": 200,
            "body": json.dumps("No signals"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    else:
        return {
            "statusCode": 200,
            "body": json.dumps(reduce_tf(all_signals, timeframe_data)),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

def get_data(table, ttl):
    dynamo_table = dynamodb.Table(table)
    try:
        # Scan the table for all datapoints
        results = dynamo_table.scan()
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in results:
            # Turn the returned object into a JSON string,
            # and pass it to pandas to make it readable for TA
            for i in range(len(results['Items'])):
                results['Items'][i]['t'] = results['Items'][i]['t'] - ttl
            print(json.dumps(results['Items']))
            return json.dumps(results['Items'])
        else:
            return []

def run_indicator(indicator):
    timeframe = indicator['timeframe']
    if indicator['timeframe'] == 'month': candles = month_candles
    elif indicator['timeframe'] == 'week': candles = week_candles
    elif indicator['timeframe'] == 'day': candles = day_candles
    elif indicator['timeframe'] == 'four_hour': candles = four_hour_candles
    elif indicator['timeframe'] == 'hour': candles = hour_candles
    elif indicator['timeframe'] == 'fifteen_minute': candles = fifteen_minute_candles
    elif indicator['timeframe'] == 'minute': candles = minute_candles

    print(candles)

    if not candles:
        print('not candle... :(')
        return []
    else:
        candles = pd.read_json(candles)

    print(candles)

    indicator_data = match_indicator(indicator['indicator'], indicator['params'], candles, timeframe)

    print(indicator_data)
    if indicator_data:
        return ([{
            'indicator': indicator['indicator'],
            'tf': timeframe,
            'sig': 'hold',
            'str': 0,
            'start': candles['t'][0]
        },
        indicator_data])


def reduce_tf(all_signals, tf_signals):
    final_signals = []
    tf_sig_len = len(tf_signals)

    balance = 100000
    prev_buy = 0
    roi = 0
    total_roi = 0
    roi_count = 0

    overall_sig = "hold"

    for signal in all_signals:
        current_sig = signal['sig']
        current_tf = signal['tf']
        if current_sig != overall_sig:
            str_count = 0
            str_total = 0
            for i in range(tf_sig_len):
                if current_tf == tf_signals[i]['tf'] and signal['indicator'] == tf_signals[i]['indicator']:
                    if current_sig != tf_signals[i]['sig']:
                        tf_signals[i]['sig'] = current_sig
                        tf_signals[i]['str'] = signal['str']
                        str_total += signal['str']
                        str_count += 1
                else:
                    if current_sig != tf_signals[i]['sig'] and signal['time'] >= tf_signals[i]['start']:
                        break
                    elif tf_signals[i]['str'] != 0:
                        str_total += tf_signals[i]['str']
                        str_count += 1

                if i == (tf_sig_len - 1):
                    overall_sig = current_sig
                    transaction = (round(((str_total / str_count) * Decimal(signal['price'])), 10))
                    if (current_sig == 'buy'):
                        balance = round((balance - transaction), 2)
                        prev_buy = transaction
                        final_signals.append({
                            'sig': 'buy',
                            'time': signal['time'],
                            'amt': transaction
                        })

                    else:
                        balance = round((balance + transaction), 2)
                        if (prev_buy != 0):
                            roi = round((((transaction - prev_buy) / prev_buy) * 100), 6)
                            total_roi += roi
                            roi_count += 1

                        final_signals.append({
                            'sig': 'sell',
                            'time': signal['time'],
                            'amt': transaction,
                            'roi': roi
                        })
    
    if (roi_count == 0):
        final_signals.append({
            'bal': balance,
            'avg_roi': 0
        })
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    print('final signals: ', final_signals)

    return final_signals

# A simple function to call the indicators.
# This may be better done with a struct
def match_indicator(indicator, params, candles, timeframe):
    if (indicator == 'rsi'):
        return rsi(params, candles, timeframe)
    elif (indicator == 'macd'):
        return macd(candles)
    elif (indicator == 'bb'):
        return bb(candles)
    else:
        return []



# VOLUME

# Accumulation/Distribution Index
def adi():
    print('adi')

# Chaikin Money Flow
def cmf():
    print('cmf')

# Ease of Movement
def emv():
    print('emv')

# Force Index
def fi():
    print('fi')

# Negative Volume Index
def nvi():
    print('nvi')

# On-Balance Volume
def obv():
    print('obv')

# Volume-price Trend
def vpt():
    print('vpt')



# VOLATILITY

# Average True Range
def atr():
    print('atr')

# Bollinger Bands
def bb(data):
    signals = []

    for i in range(len(data)):
        if (data['c'][i] < 7000):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8500):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

# Donchian Channel
def dc():
    print('dc')

# Keltner Channel
def kc():
    print('kc')



# TREND

# Average Directional Movement Index
def adx():
    print('adx')

# Commodity Channel Index
def cci():
    print('cci')

# Detrended Price Oscillator
def dpo():
    print('dpo')

# Ichimoku Kinkō Hyō
def ichimoku():
    print('Ichimoku')

# KST Oscillator
def kst():
    print('kst')

# Moving Average Convergence Divergence
def macd(data):
    signals = []

    for i in range(len(data)):
        if (data['c'][i] < 6500):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8000):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

# Mass Index
def mi():
    print('mi')

# Parabolic Stop And Reverse
def parabolic_sar():
    print('parabolic_sar')

# Trix
def trix():
    print('trix')

# Vortex Indicator
def vi():
    print('vi')



# MOMENTUM

# Awesome Oscillator
def ao():
    print('ao')

# Kaufman's Adaptive Moving Average
def kama():
    print('kama')

# Money Flow Index
def mfi():
    print('mfi')

# Relative Strength Index
def rsi(params, candles, timeframe):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)

    signals = []
    last_signal = 'hold'

    for i in range(len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
            if (current_rsi < params['buy'] and last_signal != 'buy'):
                last_signal = 'buy'
                signals.append({
                    'indicator': 'rsi',
                    'sig': 'buy',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((100 - current_rsi - 10) / 100), 10)
                })
            elif (current_rsi > params['sell'] and last_signal != 'sell'):
                last_signal = 'sell'
                signals.append({
                    'indicator': 'rsi',
                    'sig': 'sell',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((current_rsi - 10) / 100), 10)
                })

    return signals


def rsi_test(params, candles, timeframe):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)

    signals = []
    last_signal = 'hold'

    for i in range(len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
            if (current_rsi < params['buy'] and last_signal != 'buy'):
                last_signal = 'buy'
                signals.append({
                    'indicator': 'rsi',
                    'sig': 'buy',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((100 - current_rsi - 10) / 100), 10)
                })
            elif (current_rsi > params['sell'] and last_signal != 'sell'):
                last_signal = 'sell'
                signals.append({
                    'indicator': 'rsi',
                    'sig': 'sell',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((current_rsi - 10) / 100), 10)
                })

    print('rsi: ', signals)
    return signals

# Rate of Change
def roc():
    print('roc')

# Stochastic Oscillator
def sr():
    print('sr')

# True strength index
def tsi():
    print('tsi')

# Ultimate Oscillator
def uo():
    print('uo')

# Williams %R
def wr():
    print('wr')



# OTHERS

# Daily Return
def dr():
    print('dr')

# Daily Log Return
def dlr():
    print('dlr')

# Cumulative Return
def cr():
    print('cr')