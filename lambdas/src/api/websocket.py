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
    connectionID = event["requestContext"].get("connectionId")

    symbol = 'BTC'
    timestamp = int(time.time())
    ttl = 157680000
    gap = 86400
    timeframe = 100
    table = 'BTC_day'

    # Get the most recent data
    table = dynamodb.Table(table)
    response = table.query(
            KeyConditionExpression = Key('s').eq(symbol) & Key('t').gt((timestamp + ttl) - (gap * timeframe))
        )
    print(response)
    items = response.get("Items", [])
    print(items)

    # Extract the relevant data and order chronologically
    prices = [{"h": x["h"], "l": x["l"], "o": x["o"], "c": x["c"]}
            for x in items]

    print(prices)

    # Send them to the client who asked for it
    data = {"prices": prices}
    _send_to_connection(connectionID, data, event)

    return {
        "statusCode": 200,
        "body": json.dumps("Sent prices.")
    }


def _send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
            endpoint_url = "https://" + event["requestContext"]["domainName"] +
                    "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8'))