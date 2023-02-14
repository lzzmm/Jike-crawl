# -*- coding:utf8 -*-
# create at: 2023-01-15T10:07:08Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo

from utils import *
from common import CURR_TIME, BASE_TIME

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
    x = op_post(payload)
    warn(id, x, x.json())


def clear(post_path, start_time, end_time, limit=None):
    # DONE: clear all posts in time range
    # Priority: low, because you can easily delete your account directly
    # DONE: time range or other condition
    warn("There will be some warn(s) when truly removing post(s).")

    with open(post_path, 'r', encoding="utf8") as f:
        count = 0
        line = f.readline()
        while (line):
            x = json.loads(line)
            line = f.readline()

            time = datetime.strptime(
                x['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())

            if time > end_time:
                continue

            if (limit != None and count >= limit) or time < start_time:
                break

            count += 1
            id = x['id']
            info("processing", id, "created at", time)
            ################# DANGER ZONE ##################
            ################################################
            # uncomment next line to remove all your posts #
            # remove(id) # remove posts by id              #
            ################################################

        done(count, "record(s) operated.")


if __name__ == "__main__":
    CURR_TIME = datetime.now(GMT8())
    post_path = os.path.join(DIR_PATH, "data/posts.json")

    # operate posts created during 2021/12/01 and 2021/12/31
    # class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
    # start_time = datetime(2021, 1, 1, tzinfo=GMT8())
    # end_time = datetime(2021, 12, 31, tzinfo=GMT8())

    # operate posts created before 30 days ago
    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # time_delta = timedelta(days=30)
    # end_time = CURR_TIME - time_delta

    # operate all posts
    start_time = BASE_TIME  # datetime
    end_time = CURR_TIME   # datetime
    limit = None  # int or None

    clear(post_path, start_time, end_time, limit)
