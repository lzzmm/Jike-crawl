# -*- coding:utf8 -*-
# create at: 2023-01-15T10:07:08Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo

from utils import handle_errors, headers, cookies, UTC, GMT8

BASE_TIME = datetime(2015, 3, 28, tzinfo=GMT8())  # Jike 1.0 online
CURR_TIME = datetime.now(GMT8())  # current time

dir_path = os.path.dirname(os.path.dirname(__file__))

url = "https://web-api.okjike.com/api/graphql"

payload = {
    "operationName": "RemoveMessage",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    },
    "query": "mutation RemoveMessage($id: ID!, $messageType: MessageType!) {\n  removeMessage(messageType: $messageType, id: $id) {\n    toast\n    __typename\n  }\n}\n"
}


def remove(id):
    """
    remove a post with id
    ---
    args: 
    - id: id of the post
    """
    payload["variables"]["id"] = id

    try:
        x = requests.post(url, cookies=cookies,
                          headers=headers,
                          data=json.dumps(payload))
        print(x, x.json())
    except requests.exceptions.ConnectionError as e:
        print("Connection error", e.args)

    if ('errors' in x.json()):
        handle_errors(x, halt=False)
    return x


def clear(post_path, start_time, end_time):
    # DONE: clear all posts in time range
    # Priority: low, because you can easily delete your account directly
    # DONE: time range or other condition
    with open(post_path, 'r', encoding="utf8") as f:
        count = 0
        line = f.readline()
        while (line):
            x = json.loads(line)
            line = f.readline()

            time = datetime.strptime(
                x['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())

            if time < start_time or time > end_time:
                continue

            count += 1
            id = x['id']
            print(id, time)
            ################# DANGER ZONE ##################
            ################################################
            # uncomment next line to remove all your posts #
            # remove(id) # remove posts by id              #
            ################################################

        print(count, "record(s) operated.")


if __name__ == "__main__":
    post_path = os.path.join(dir_path, "data/posts.json")

    # class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
    # start_time = datetime(2021, 1, 1, tzinfo=GMT8())
    # end_time = datetime(2021, 12, 31, tzinfo=GMT8())
    # operate posts created during 2021/12/01 and 2021/12/31

    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # time_delta = timedelta(days=30)
    # end_time = CURR_TIME - time_delta
    # operate posts created before 30 days ago

    start_time = BASE_TIME  # datetime
    end_time = CURR_TIME   # datetime
    # operate all posts

    clear(post_path, start_time, end_time)
