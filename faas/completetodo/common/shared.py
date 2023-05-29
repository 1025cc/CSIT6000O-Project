import calendar
import datetime
import os
import uuid
from decimal import Decimal
from http.cookies import SimpleCookie

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}

class NotFoundException(Exception):
    pass


def get_user_id(event_headers):
    """
    Retrieve user_id from cookies if it exists, otherwise set and return it
    """
    cookie = SimpleCookie()
    try:
        cookie.load(event_headers["cookie"])
        user_cookie = cookie["userID"].value
        generated = False
    except KeyError:
        user_cookie = str(uuid.uuid4())
        generated = True

    return user_cookie, generated

def get_headers(user_id):
    """
    Get the headers to add to response data
    """
    headers = HEADERS
    cookie = SimpleCookie()
    cookie["userID"] = user_id
    cookie["userID"]["max-age"] = (60 * 60) * 24 * 7 # 7 day
    cookie["userID"]["httponly"] = True
    cookie["userID"]["path"] = "/"
    headers["Set-Cookie"] = cookie["userID"].OutputString()

    return headers
