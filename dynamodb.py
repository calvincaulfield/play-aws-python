import boto3
from botocore.config import Config
import base64

def do():
    my_config = Config(
        region_name="us-east-2", retries={"max_attempts": 1, "mode": "standard"}
    )

    ddb = boto3.resource("dynamodb", config=my_config)
    table = ddb.Table('test')
    n = 123
    m = str(n)
    table.put_item(
        Item={
            'a': "key",
            'number': m
        },
    )

    # ddb.put

if __name__ == "__main__":
    do()
