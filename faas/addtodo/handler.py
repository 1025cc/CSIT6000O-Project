from pymongo import MongoClient
import json
import os
import sys

script_dir = os.path.dirname(__file__)
mymodule_dir = os.path.join(script_dir, 'common')
sys.path.append(mymodule_dir)

from shared import (
    NotFoundException,
    get_user_id,
    get_headers,
)

mongodb_service_url = os.environ["MONGODB_SERVICE_URL"]

mongo_client = MongoClient(host=mongodb_service_url,
        port=27017,
        username='admin',
        password='admin')

mydb = mongo_client['test']
mycol = mydb['list']


def handle(event, context):
    """handle a request to the function
    Args:
        req (str): request body
    """
    request_payload = json.loads(event.body.decode('utf-8'))
    # print(request_payload)
    item_id = request_payload["itemId"]
    content = request_payload["content"]
    user_id, _ = get_user_id(event.headers)

    pk = f"user#{user_id}"

    item = {
        "pk": pk,
        "sk": f"item#{item_id}",
        "state":1,
        "content": content
    }

    mycol.insert_one(item)

    
    return {
        "statusCode": 200,
        "headers": get_headers(user_id),
        "body": json.dumps(
            {"itemId": item_id, "message": "item added to list"}
        ),
    }

