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
