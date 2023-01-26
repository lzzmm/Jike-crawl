# -*- coding:utf8 -*-
# create at: 2023-01-15T09:33:25Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo

from utils import handle_errors, save_json, save_pics, headers, cookies, UTC, GMT8
from delete_posts import clear


dir_path = os.path.dirname(os.path.dirname(__file__))


url = "https://web-api.okjike.com/api/graphql"


BASE_TIME = datetime(2015, 3, 28, tzinfo=GMT8())  # Jike 1.0 online
CURR_TIME = datetime.now(GMT8())  # current time


def crawl(url, cookies, headers, payload):
    """
    crawl data
    ---
    args: 
    - url
    - cookies
    - headers
    - payload
    - return: response
    """
    try:
        x = requests.post(url, cookies=cookies,
                          headers=headers,
                          data=json.dumps(payload))
        print(x)
    except requests.exceptions.ConnectionError as e:
        print("Connection error", e.args)

    # The "has_key" method has been removed in Python 3
    while 'errors' in x.json():
        handle_errors(x)
        x = crawl(url, cookies, headers, payload)

    return x


def proc_node(node, path, mode, start_time, end_time, end, record_count, b_save_pics=False, record_count_limit=None):
    """
    process notification/post
    ---
    args:
    - node: node object to process
    - path: path to save object
    - mode: mode to save object
    - start_time: start time of object to be saved
    - end_time: end time of object to be saved
    - end: bool, end of save, so stop request
    - record_count: number of records saved
    - record_count_limit: limit number of records to be saved
    """

    time = datetime.strptime(
        node['createdAt'], "%Y-%m-%dT%X.%fZ").astimezone(UTC())

    if time >= start_time and time <= end_time:
        save_json(node, path, mode) # TODO: write to a temp file and at last concat 
        if b_save_pics and ("pictures" in node) and len(node["pictures"]) != 0:
            save_pics(node)
        record_count += 1

    if (record_count_limit != None and record_count >= record_count_limit) or time < start_time:
        end = True

    return end, record_count


def crawl_notifications(path, mode="a", b_save_pics=False, record_count_limit=None, start_time=BASE_TIME, end_time=CURR_TIME):
    """
    loop and crawl all/num notifications from start_time to end_time and save into database/file
    ---
    args:
    - path: file path 
    - num: number of records to crawl
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """

    payload = {
        "operationName": "ListNotification",
        "variables": {},
        "query": open(os.path.join(dir_path, "query/query_notifications.txt")).read()
    }

    request_count = 0
    record_count = 0
    end = False

    x = crawl(url, cookies, headers, payload)

    request_count += 1
    loadMoreKey = x.json()[
        "data"]["viewer"]["notifications"]["pageInfo"]["loadMoreKey"]
    print(request_count, loadMoreKey)

    for node in x.json()["data"]["viewer"]["notifications"]["nodes"]:
        end, record_count = proc_node(node,
                                      path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)
        if end == True:
            break

    while end != True and loadMoreKey != None:  # 'hasNextPage': True

        request_count += 1
        payload["variables"]["loadMoreKey"] = loadMoreKey

        x = crawl(url, cookies, headers, payload)

        loadMoreKey = x.json()[
            "data"]["viewer"]["notifications"]["pageInfo"]["loadMoreKey"]
        print(request_count, loadMoreKey)

        # if x.json()["data"]["viewer"]["notifications"]["nodes"]:
        for node in x.json()["data"]["viewer"]["notifications"]["nodes"]:
            end, record_count = proc_node(
                node, path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)
            if end == True:
                break

    print(request_count, "request(s) was(were) sent.")
    print(record_count, "record(s) saved.")


def crawl_posts(user_id, path, mode="a", b_save_pics=False, record_count_limit=None, start_time=BASE_TIME, end_time=CURR_TIME):
    """
    loop and crawl all notifications and save into database/file
    ---
    args:
    - path: file path 
    - user_id: Jike user id
    - num: number of records to crawl
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """

    payload = {
        "operationName": "UserFeeds",
        "query": open(os.path.join(dir_path, "query/query_user_feeds.txt")).read(),
        "variables": {
            "username": user_id
        }
    }

    end = False
    request_count = 0
    record_count = 0

    x = crawl(url, cookies, headers, payload)

    request_count += 1

    loadMoreKey = x.json()[
        "data"]["userProfile"]["feeds"]["pageInfo"]["loadMoreKey"]
    print(request_count, loadMoreKey)

    for node in x.json()["data"]["userProfile"]["feeds"]["nodes"]:
        end, record_count = proc_node(node,
                                      path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)
        if end == True:
            break

    while end != True and loadMoreKey != None:  # 'hasNextPage': True
        request_count += 1
        payload["variables"]["loadMoreKey"] = loadMoreKey

        x = crawl(url, cookies, headers, payload)

        loadMoreKey = x.json()[
            "data"]["userProfile"]["feeds"]["pageInfo"]["loadMoreKey"]
        print(request_count, loadMoreKey)

        # if x.json()["data"]["userProfile"]["feeds"]["nodes"]:
        for node in x.json()["data"]["userProfile"]["feeds"]["nodes"]:
            end, record_count = proc_node(node,
                                          path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)
            if end == True:
                break

    print(request_count, "request(s) was(were) sent.")
    print(record_count, "record(s) saved.")


if __name__ == "__main__":
    noti_path = os.path.join(dir_path, "data/notifications.json")
    post_path = os.path.join(dir_path, "data/posts.json")

    ##################################################
    # ATTENTION: Replace with your own Jike user id. #
    user_id = "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
    ##################################################

    b_save_pics = False # Bool

    # class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
    # start_time = datetime(2021, 1, 1, tzinfo=GMT8())
    # end_time = datetime(2021, 1, 10, tzinfo=GMT8())
    # operate posts created during 2021/12/01 and 2021/12/31

    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # time_delta = timedelta(days=30)
    # end_time = CURR_TIME - time_delta
    # operate posts created before 30 days ago

    noti_start_time = BASE_TIME  # datetime
    noti_end_time = CURR_TIME   # datetime
    noti_record_limit = None    # int or None
    # crawl_notifications(
    # noti_path, "a", False, noti_record_limit, noti_start_time, noti_end_time)

    post_start_time = BASE_TIME  # datetime
    post_end_time = CURR_TIME   # datetime
    post_record_limit = None    # int or None
    crawl_posts(user_id, post_path, "a", b_save_pics,
                post_record_limit, post_start_time, post_end_time)

    # goto "delete_posts.py" and manually enable remove()
    # clear(post_path)
