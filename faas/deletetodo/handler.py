import json
import os
import sys

from pymongo import MongoClient

script_dir = os.path.dirname(__file__)
mymodule_dir = os.path.join(script_dir, 'common')
sys.path.append(mymodule_dir)

mongodb_service_url = os.environ["MONGODB_SERVICE_URL"]

from shared import (
    NotFoundException,
    get_user_id,
    get_headers,
)


mongo_client = MongoClient(host=mongodb_service_url,
        port=27017,
        username='admin',
        password='admin')

mydb = mongo_client['test']
mycol = mydb['list']

def handle(event, context):

    request_payload = json.loads(event.body.decode('utf-8'))
    item_id = request_payload["itemId"]
    # content = request_payload["content"]
    user_id, _ = get_user_id(event.headers)

    pk = f"user#{user_id}"
    
    key = {
        "pk": pk,
        "sk": f"item#{item_id}",
    }

    data = {
            "$set": {
                "state":3
            }
        }

    mycol.update_one(key, data)

    return {
            "statusCode": 200,
            "headers": get_headers(user_id),
            "body": json.dumps({"itemId": item_id, "message": "delete item"}, default=str),
            }

