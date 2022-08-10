import boto3
from botocore.config import Config


class DynamoDB:
    def __init__(self, region_name: str = "us-east-1", table_name: str = None):
        config = Config(retries=dict(max_attempts=25))
        self._dynamodb = boto3.resource(
            "dynamodb", region_name=region_name, config=config
        )
        self._table_name = table_name
        self._table = self._dynamodb.Table(table_name) if table_name else None

    def put_item(self, item):
        return self._table.put_item(Item=item)

    def delete_item(self, key):
        return self._table.delete_item(Key=key)

    def get_item(self, key):
        response = self._table.get_item(Key=key)
        return response["Item"]

    def update_item(self, key_dict: dict, fields_to_update_list: [tuple]):
        """
        key_dict is a dictionary of field:value identifying the key for the field
        fields_to_update_list should be a list of tuples in format of [(field1, new_value1), (field2, new_value2)]
        """
        update_expression = ", ".join(
            [
                f"{field_tuple[0]} = :{i}"
                for i, field_tuple in enumerate(fields_to_update_list)
            ]
        )
        attribute_values = {
            f":{i}": field_tuple[1]
            for i, field_tuple in enumerate(fields_to_update_list)
        }
        return self._table.update_item(
            Key=key_dict,
            UpdateExpression=f"SET {update_expression}",
            ExpressionAttributeValues=attribute_values,
            ReturnValues="UPDATED_NEW",
        )

    def get_all_table_items(self, table_name: str = None):
        """
        Return a dictionary of all items in table
        if table name is specified,
        we read the items from table_name instead of self._table
        """
        if table_name:
            return self._get_all_table_name_items(table_name=table_name)

        response = self._table.scan()
        return response["Items"]

    def _get_all_table_name_items(self, table_name: str) -> List:

        # all_items = db_client.scan()
        # Important: scan is not able to read too many items without paging
        # put below the aws db method that you want to call instead of scan
        paginator = self._dynamodb.meta.client.get_paginator("scan")
        operation_parameters = {"TableName": table_name}
        pages = paginator.paginate(**operation_parameters)
        items = []
        for page in pages:
            for i in page["Items"]:
                item = dict(list(i.items()))
                items.append(item)
        return items

    def get_stacks_by_type(self, stack_type):
        """
        Return a list of all stacks with the specified type
        """
        stacks = []
        table = self.get_all_table_items()
        for item in table:
            if item.get("sponsor_stack_type") == stack_type:
                stacks.append(item)
        return stacks
