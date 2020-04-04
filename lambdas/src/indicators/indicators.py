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
    if (event['queryStringParameters'] == None):
        return {
            "statusCode": 502,
            "body": "No parameters given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Load the payload into a usable format
    data = json.loads(event['queryStringParameters']['vals'])

    if not data:
        return {
            "statusCode": 502,
            "body": "No data given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Remove the array of timeframes from the data
    timeframes = data[0]
    data.pop(0)

    if not data:
        return {
            "statusCode": 502,
            "body": "Data is in incorrect format",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    all_signals = []
    final_signals = []

    # Condense all signals of all indicators for each timeframe given
    # into a single array, and append that array to the main array
    if ('month' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_month'), 'month')
        if signals:
            all_signals.append(signals)
    if ('week' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_week'), 'week')
        if signals:
            all_signals.append(signals)
    if ('day' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_day'), 'day')
        if signals:
            all_signals.append(signals)
    if ('four_hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_four_hour'), 'four_hour')
        if signals:
            all_signals.append(signals)
    if ('hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_hour'), 'hour')
        if signals:
            all_signals.append(signals)
    if ('fifteen_minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_fifteen_minute'), 'fifteen_minute')
        if signals:
            all_signals.append(signals)
    if ('minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_minute'), 'minute')
        if signals:
            all_signals.append(signals)
    if ('second' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_second'), 'second')
        if signals:
            all_signals.append(signals)

    if not all_signals:
        return {
            "statusCode": 200,
            "body": "No signals",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    a_s_length = len(all_signals)

    if (a_s_length == 1):
        return {
            "statusCode": 200,
            "body": json.dumps(one_tf(all_signals[0])),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    else:
        return {
            "statusCode": 200,
            "body": json.dumps(multi_tf(all_signals, a_s_length)),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

def get_data(table):
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
            return json.dumps(results['Items'])
        else:
            return []

def condense_timeframe(data, candles, timeframe):
    # Error catching for get_data
    if not candles:
        return []
    else:
        candles = pd.read_json(candles)

    timeframe_data = []
    timeframe_signals = []

    # If an indicator is requested on this timeframe,
    # append that indicator's data to an array
    for i in range(0, len(data)):
        if (data[i]['timeframe'] == timeframe):
            indicator = match_indicator(data[i]['indicator'], candles)
            if indicator:
                timeframe_data.append(indicator)

    # Error catching for no signals returned
    if not timeframe_data:
        return []

    t_d_length = len(timeframe_data)
    
    # If only one indicator returned signals
    # make an array of signals different from the
    # one before and the one after it
    if (t_d_length == 1):
        for i in range(0, len(candles)):
            signal = timeframe_data[0][i]['sig']
            if ((not timeframe_signals) or (signal != timeframe_signals[len(timeframe_signals) - 1]['sig'])):
                timeframe_signals.append({
                    'sig': signal,
                    'str': timeframe_data[0][i]['str'],
                    'time': int(candles['t'][i]),
                    'price': int(candles['c'][i])
                })

    # Go through each indicator's signal at a given index.
    # If all signals match at one index, calculate the avg
    # strength of all those signals and append it to a final array
    else:
        strength = 0
        for i in range (0, len(candles)):
            signal = timeframe_data[0][i]['sig']
            if ((not timeframe_signals) or (signal != timeframe_signals[len(timeframe_signals) - 1]['sig'])):
                strength += timeframe_data[0][i]['str']
                for j in range (1, t_d_length):
                    if (timeframe_data[j][i]['sig'] != signal):
                        break

                    elif (j == (t_d_length - 1)):
                        final_strength = round((strength / t_d_length), 10)
                        timeframe_signals.append({
                            'sig': signal,
                            'str': final_strength,
                            'time': int(candles['t'][i]),
                            'price': int(candles['c'][i])
                        })

                        strength = 0
                        break

                    else:
                        strength += timeframe_data[j][i]['str']

    return timeframe_signals

# Function called if singal timeframe given
def one_tf(all_signals):
    final_signals = []

    balance = 100000
    prev_buy = 0
    roi = 0
    total_roi = 0
    roi_count = 0

    # Run a loop over the signals given.
    # Remove all hold signals.
    # Calculate ROI for any sell that comes after a buy.
    # Calculate transaction amounts based on strength of the signal.
    for i in range(0, len(all_signals)):
        signal = all_signals[i]['sig']
        if (signal != 'hold' and ((not final_signals) or (signal != final_signals[len(final_signals) - 1]['sig']))):
            transaction = (all_signals[i]['str'] * all_signals[i]['price'])
            if (signal == 'buy'):
                balance = round((balance - transaction), 2)
                prev_buy = transaction
                final_signals.append({
                    'sig': signal,
                    'time': all_signals[i]['time'],
                    'amt': transaction
                })

            else:
                balance = round((balance + transaction), 2)
                if (prev_buy != 0):
                    roi = (((transaction - prev_buy) / prev_buy) * 100)
                    total_roi += roi
                    roi_count += 1

                final_signals.append({
                    'sig': signal,
                    'time': all_signals[i]['time'],
                    'amt': transaction,
                    'roi': roi
                })

    if (roi_count == 0):
        final_signals.append({'bal': balance})
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    return final_signals

# Function called if singal timeframe given
def multi_tf(all_signals, a_s_length):
    final_signals = []
    a_s_record = []

    signal = all_signals[0][0]['sig']
    strength = all_signals[0][0]['str']
    str_count = 1
    timestamp = all_signals[0][0]['time']
    tf = 1
    balance = 100000
    prev_buy = 0
    roi = 0
    total_roi = 0
    roi_count = 0

    # This keeps track of the current signal being looked at
    # for each timeframe and the final signal for each timeframe.
    # This lets us not look through old data and error catches
    # going past the last index
    for i in range(0, a_s_length):
        a_s_record.append([0, len(all_signals[i])])

    # Loop through the largest timeframe's signals.
    # For each timeframe given, look at all the signals between
    # the next biggest (parent's) timeframe's current signal timestamp
    # and its next signal timestamp. Try to find a matching signal
    # for the current timeframe in that gap of its parent's.
    # If the smallest timeframe has been reached and all timeframes
    # have a signal matching within the scope of their parent,
    # calculate strength, ROI, transaction, and a new balance,
    # and append the signal to a final array
    while (a_s_record[0][0] < a_s_record[0][1]):
        if (signal != 'hold' and ((not final_signals) or (signal != final_signals[len(final_signals) - 1]['sig']))):
            if ((a_s_record[tf - 1][0] + 1) < a_s_record[tf - 1][1]):
                # If current timeframe's first signal is past its parent's next signal, send signal
                prev_too_early = all_signals[tf][0]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0] + 1]['time']
                # If current signal is past its parent's next signal
                current_too_late = all_signals[tf][a_s_record[tf][0]]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0] + 1]['time']

                if (prev_too_early):
                    final_strength = round(Decimal(strength / str_count), 10)
                    transaction = round((final_strength * round(Decimal(all_signals[tf][a_s_record[tf][0]]['price']), 6)), 2)
                    print('strength: ', strength, ' str count: ', str_count, ' final str: ', final_strength)
                    print('price: ', all_signals[tf][a_s_record[tf][0]]['price'], ' transaction: ', transaction)
                    print(all_signals[tf][a_s_record[tf][0]])
                    if (signal == 'buy'):
                        balance = round((balance - transaction), 2)
                        prev_buy = transaction
                        final_signals.append({
                            'sig': signal,
                            'time': timestamp,
                            'amt': transaction
                        })

                    else:
                        balance = round((balance + transaction), 2)
                        if (prev_buy != 0):
                            roi = (((transaction - prev_buy) / prev_buy) * 100)
                            total_roi += roi
                            roi_count += 1
                        
                        final_signals.append({
                            'sig': signal,
                            'time': timestamp,
                            'amt': transaction,
                            'roi': roi
                        })
                    a_s_record[0][0] += 1
                    tf = 1
                    signal = all_signals[0][a_s_record[0][0]]['sig']
                    strength = all_signals[0][a_s_record[0][0]]['str']
                    str_count = 1
                    timestamp = all_signals[0][a_s_record[0][0]]['time']
                    continue

                elif (current_too_late):
                    tf -= 1
                    a_s_record[tf][0] += 1
                    if (tf == 0):
                        tf = 1
                        signal = all_signals[0][a_s_record[0][0]]['sig']
                        strength = all_signals[0][a_s_record[0][0]]['str']
                        str_count = 1
                        timestamp = all_signals[0][a_s_record[0][0]]['time']
                    continue

            # If its the right signal
            if (all_signals[tf][a_s_record[tf][0]]['sig'] == signal):
                # If the signal's timestamp is >= than that of its parent's current signal
                sig_past_parent = all_signals[tf][a_s_record[tf][0]]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0]]['time']

                if ((a_s_record[tf][0] + 1) == a_s_record[tf][1]):
                    next_sig_past_parent = False
                else:
                    # If the signal's next timestamp is > than that of its parent's current signal
                    next_sig_past_parent = all_signals[tf][a_s_record[tf][0] + 1]['time'] > all_signals[tf - 1][a_s_record[tf - 1][0]]['time']
                if (sig_past_parent or next_sig_past_parent):
                    # This is the new earliest time this signal can fire
                    if (sig_past_parent):
                        timestamp = all_signals[tf][a_s_record[tf][0]]['time']
                    # If the smallest timeframe has been reached, send the signal
                    if (tf == (a_s_length - 1)):
                        final_strength = round(Decimal(strength / str_count), 10)
                        transaction = round((final_strength * round(Decimal(all_signals[tf][a_s_record[tf][0]]['price']), 6)), 2)
                        print('strength: ', strength, ' str count: ', str_count, ' final str: ', final_strength)
                        print('price: ', all_signals[tf][a_s_record[tf][0]]['price'], ' transaction: ', transaction)
                        if (signal == 'buy'):
                            balance = round((balance - transaction), 2)
                            prev_buy = transaction
                            final_signals.append({
                                'sig': signal,
                                'time': timestamp,
                                'amt': transaction
                            })

                        else:
                            balance = round((balance + transaction), 2)
                            if (prev_buy != 0):
                                roi = (((transaction - prev_buy) / prev_buy) * 100)
                                total_roi += roi
                                roi_count += 1
                            
                            final_signals.append({
                                'sig': signal,
                                'time': timestamp,
                                'amt': transaction,
                                'roi': roi
                            })
                        tf = 1
                        a_s_record[0][0] += 1
                        signal = all_signals[0][a_s_record[0][0]]['sig']
                        strength = all_signals[0][a_s_record[0][0]]['str']
                        str_count = 1
                        timestamp = all_signals[0][a_s_record[0][0]]['time']
                        continue

                    else:
                        strength += all_signals[tf][a_s_record[tf][0]]['str']
                        str_count += 1
                        tf += 1

                else:
                    a_s_record[tf][0] += 1
                    if (a_s_record[tf][0] == a_s_record[tf][1]):
                        break

            else:
                a_s_record[tf][0] += 1
                if (a_s_record[tf][0] == a_s_record[tf][1]):
                    break

        else:
            tf = 1
            a_s_record[0][0] += 1
            if (a_s_record[0][0] == a_s_record[0][1]):
                break

            signal = all_signals[0][a_s_record[0][0]]['sig']
            strength = all_signals[0][a_s_record[0][0]]['str']
            str_count = 1
            timestamp = all_signals[0][a_s_record[0][0]]['time']
            continue


    if (roi_count == 0):
        final_signals.append({'bal': balance})
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    return final_signals

# A simple function to call the indicators.
# This may be better done with a struct
def match_indicator(indicator, data):
    if (indicator == 'rsi'):
        return rsi(data)
    elif (indicator == 'macd'):
        return macd(data)
    elif (indicator == 'bb'):
        return bb(data)
    else:
        return []

def rsi(data):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = data["c"], n = 14, fillna = True)

    signals = []

    for i in range(0, len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
            if (current_rsi < 30):
                signals.append({'sig': 'buy', 'str': round(Decimal((100 - current_rsi - 10) / 100), 10)})
            elif (current_rsi > 70):
                signals.append({'sig': 'sell', 'str': round(Decimal((current_rsi - 10) / 100), 10)})
            else:
                signals.append({'sig': 'hold', 'str': 0})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

def macd(data):
    signals = []

    for i in range(0, len(data)):
        if (data['c'][i] < 6500):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8000):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

def bb(data):
    signals = []

    for i in range(0, len(data)):
        if (data['c'][i] < 7000):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8500):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals


# Volume

# Accumulation/Distribution Index (ADI)
# On-Balance Volume (OBV)
# Chaikin Money Flow (CMF)
# Force Index (FI)
# Ease of Movement (EoM, EMV)
# Volume-price Trend (VPT)
# Negative Volume Index (NVI)


# Volatility

# Average True Range (ATR)
# Bollinger Bands (BB)
# Keltner Channel (KC)
# Donchian Channel (DC)


# Trend

# Moving Average Convergence Divergence (MACD)
# Average Directional Movement Index (ADX)
# Vortex Indicator (VI)
# Trix (TRIX)
# Mass Index (MI)
# Commodity Channel Index (CCI)
# Detrended Price Oscillator (DPO)
# KST Oscillator (KST)
# Ichimoku Kinkō Hyō (Ichimoku)
# Parabolic Stop And Reverse (Parabolic SAR)


# Momentum

# Money Flow Index (MFI)
# Relative Strength Index (RSI)
# True strength index (TSI)
# Ultimate Oscillator (UO)
# Stochastic Oscillator (SR)
# Williams %R (WR)
# Awesome Oscillator (AO)
# Kaufman's Adaptive Moving Average (KAMA)
# Rate of Change (ROC)


# Others

# Daily Return (DR)
# Daily Log Return (DLR)
# Cumulative Return (CR)