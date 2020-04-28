import time
import simplejson as json

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

def connect(event, context):
    print("in connect")
    print(event)
    connectionID = event["requestContext"].get("connectionId")
    table = dynamodb.Table('websocket_connections')

    # Add connectionID to the database on a connection
    if event["requestContext"]["eventType"] == "CONNECT":
        table.put_item(Item={"ConnectionID": connectionID})

        return {
            "statusCode": 200,
            "body": json.dumps("Connect successful.")
        }

    # Remove the connectionID from the database on a disconnection
    elif event["requestContext"]["eventType"] == "DISCONNECT":
        table.delete_item(Key={"ConnectionID": connectionID})
        
        return {
            "statusCode": 200,
            "body": json.dumps("Disconnect successful.")
        }

    else:
        return {
            "statusCode": 500,
            "body": json.dumps("Unrecognized eventType.")
        }

def get_websocket_prices(event, context):
    print("in prices")
    print(event)
    print(event['body'])
    connectionID = event["requestContext"].get("connectionId")

    symbol = event["body"]["symbol"]
    print('symbol: ', symbol)
    table = dynamodb.Table(event["body"]["table"])
    ttl = event["body"]["ttl"]
    gap = event["body"]["gap"]
    datapoints = event["body"]["datapoints"]

    timestamp = int(time.time())

    try:
        # Scan the table for all datapoints
        if datapoints > 0:
            results = table.query(
                KeyConditionExpression = Key('s').eq(symbol) & Key('t').gt((timestamp + ttl) - (gap * datapoints))
            )
        else:
            results = table.scan()
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in results:
            # Make equal to current time
            for item in results['Items']:
                item['t'] = item['t'] - ttl

            # Extract the relevant data and order chronologically
            prices = [{'t': item['t'], 'h': item['h'], 'l': item['l'], 'o': item['o'], 'c': item['c']}
                    for item in results['Items']]
            print('prices 1: ', prices)

            prices.insert(0, 'table')
            print('prices 2: ', prices)

            # Send them to the client who asked for it
            data = {"prices": prices}
            _send_to_connection(connectionID, data, event)
            return {
                "statusCode": 200,
                "body": json.dumps("Sent prices.")
            }

        else:
            return {
                "statusCode": 502,
                "body": json.dumps("No data returned.")
            }


def get_dynamo_table(symbol, table, timestamp, ttl, gap, datapoints):
    dynamo_table = dynamodb.Table(table)

    try:
        # Scan the table for all datapoints
        if datapoints > 0:
            results = dynamo_table.query(
                KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + ttl) - (gap * datapoints))
            )
        else:
            results = dynamo_table.scan()
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in results:
            # Turn the returned object into a JSON string,
            # and pass it to pandas to make it readable for TA
            for item in results['Items']:
                item['t'] = item['t'] - ttl

            prices = [{'t': item['t'], 'h': item['h'], 'l': item['l'], 'o': item['o'], 'c': item['c']}
                    for item in results['Items']]

            return prices

        else:
            return []


def _send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
            endpoint_url = "https://" + event["requestContext"]["domainName"] +
                    "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8'))