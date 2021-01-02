from shared.aws import DynamoDB

class CheckSharedParameters:
    def get_handler(self, actions: [str]):
        return [
            item.get("handler")
            for item in DynamoDB.get_all_table_items("api_actions")
            if bool(set(actions) & set(item.get("actions")))
        ]

    def check_parameters(self, params: [dict]) -> (str, list):
        if not self.params:
            return "No parameters given.", []
        if not self.params.get("actions"):
            return "No actions requested.", []

        handler = self.get_handler(self.params.get("actions"))
        if not handler or len(handler) > 1:
            return "Could not find handler associated with requested actions.", []

        return None, handler[0]

        

# class CheckAnalysisParameters:
#     def __init__(self, region_name: str = "us-east-1", table_name: str = None):
#         config = Config(retries=dict(max_attempts=25))
#         self._dynamodb = boto3.resource(
#             "dynamodb", region_name=region_name, config=config
#         )
#         self._table_name = table_name
#         self._table = self._dynamodb.Table(table_name) if table_name else None

#     def put_item(self, item):
#         return self._table.put_item(Item=item)