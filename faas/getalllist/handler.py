import json
import os
import sys

from pymongo import MongoClient

script_dir = os.path.dirname(__file__)
mymodule_dir = os.path.join(script_dir, 'common')
sys.path.append(mymodule_dir)

from shared import (
    handle_decimal_type
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
    user_id, generated = get_user_id(event.headers)
    key_string = f"user#{user_id}"
   # generated = False
    # will change later

    if generated:
        item_list = []
    else:
        q = {'pk':key_string}
        item_list = list(mycol.find(q))
   # all_product = list(mycol.find())   
    for item in product_list:
        item.update(
            (k, v.replace("item#", "")) for k, v in item.items() if k == "sk"
        )
    return {
        "statusCode": 200,
        "headers": get_headers(user_id),
        "body": json.dumps({"products": item_list,}, default = str)
    }
