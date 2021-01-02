import simplejson as json
from importlib import import_module

from parameters import CheckSharedParameters

HEADERS = {"Access-Control-Allow-Origin": "*"}


def analysis_handler(event, context):
    invalid_parameters, handler = CheckSharedParameters.check_parameters(
        event.get("queryStringParameters")
    )

    if invalid_parameters:
        return {
            "statusCode": 400,
            "body": json.dumps(invalid_parameters),
            "headers": HEADERS,
        }

    handler_module = import_module(f"action-handler")
    handler_class = getattr(handler_module, f"{handler}Handler")
    handler_instance = handler_class()

    code, body = handler_instance.handle(event.get("queryStringParameters"))
    return {
        "statusCode": code,
        "body": body,
        "headers": HEADERS,
    }
