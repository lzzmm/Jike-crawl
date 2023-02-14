# -*- coding:utf8 -*-
# create at: 2023-01-15T09:33:25Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime

from utils import *
from common import *


DIR_PATH = os.path.dirname(os.path.dirname(__file__))


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
        node['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())

    debug(time)

    # TODO: this should not be here and should be outside this function
    # time should not euqal to start_time which leads to re-add of first node
    if time > start_time and time <= end_time:
        save_json(node, path, mode)
        if b_save_pics and ("pictures" in node) and len(node["pictures"]) != 0:
            save_pics(node)
        record_count += 1

    if (record_count_limit != None and record_count >= record_count_limit) or (time <= start_time):
        end = True

    return end, record_count


def crawl_notifications(path, mode="a", b_save_pics=False, record_count_limit=None, start_time=BASE_TIME, end_time=datetime.now(GMT8()), update=True):
    """
    loop and crawl all/num notifications from start_time to end_time and save into database/file
    TODO: Incremental update like "crawl_posts"
    ---
    args:
    - path: file path 
    - num: number of records to crawl
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """
    debug("crawl_notifications(%s, %s)" % (path, mode))

    payload = PAYLOAD_LIST_NOTIFICATION

    end = False
    add_data = False
    is_first_node = True
    first_node_inserted = False
    request_count = 0
    record_count = 0
    origin_path = path
    first_node = {}

    if update == True:
        try:
            with open(path, 'r', encoding="utf8") as f:
                line = f.readline()
                response = json.loads(line)
                if 'createdAt' in response:
                    start_time = datetime.strptime(
                        response['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
                    info("Read record(s) from", start_time)
                    path = os.path.join(
                        DIR_PATH, "data/temp-new-data-info.json")
                    os.remove(path) if os.path.isfile(path) else ...
                    add_data = True
        except Exception as e:
            warn(e.args)

    while True:

        response = crawl(API_GRAPHQL, COOKIES, HEADERS, payload)
        request_count += 1

        loadMoreKey = response.json()[
            "data"]["viewer"]["notifications"]["pageInfo"]["loadMoreKey"]
        payload["variables"]["loadMoreKey"] = loadMoreKey
        info("sending request", request_count, loadMoreKey)

        for node in response.json()["data"]["viewer"]["notifications"]["nodes"]:

            end, record_count = proc_node(
                node, path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)

            if end == True:
                break

        if end == True or loadMoreKey == None:
            break

    if add_data == True:

        with open(origin_path, 'r', encoding='utf-8') as ori_f:
            with open(path, 'a', encoding='utf-8') as new_f:
                new_f.write(ori_f.read())

        os.remove(origin_path)
        os.rename(path, origin_path)

    done(request_count, "request(s) sent.")
    done(record_count, "record(s) saved.")


def crawl_posts(user_id, path, mode="a", b_save_pics=False, record_count_limit=None, start_time=BASE_TIME, end_time=CURR_TIME, update=True):
    """
    loop and crawl all notifications and save into database/file
    TODO: function too long! rewrite it!
    ---
    args:
    - path: file path 
    - user_id: Jike user id
    - num: number of records to crawl
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """

    debug("crawl_posts(%s, %s, %s)" % (user_id, path, mode))
    info("From:", start_time, "to:", end_time)

    payload = PAYLOAD_USER_FEEDS
    payload["variables"]["username"] = user_id

    end = False
    add_data = False
    is_first_node = True
    first_node_inserted = False
    request_count = 0
    record_count = 0
    origin_path = path
    first_node = {}

    if update == True:
        try:
            with open(path, 'r', encoding="utf8") as f:
                line = f.readline()
                response = json.loads(line)
                if 'createdAt' in response:
                    start_time = datetime.strptime(
                        response['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
                    info("Read record(s) from", start_time)
                    path = os.path.join(DIR_PATH, "data/temp-new-data.json")
                    os.remove(path) if os.path.isfile(path) else ...
                    add_data = True
        except Exception as e:
            warn(e.args)

    while True:

        response = crawl(API_GRAPHQL, COOKIES, HEADERS, payload)
        request_count += 1

        loadMoreKey = response.json()[
            "data"]["userProfile"]["feeds"]["pageInfo"]["loadMoreKey"]
        payload["variables"]["loadMoreKey"] = loadMoreKey
        info("sending request", request_count, loadMoreKey)

        for node in response.json()["data"]["userProfile"]["feeds"]["nodes"]:
            if is_first_node == True:
                first_node = node
                is_first_node = False
                continue
            elif (not first_node_inserted) and datetime.strptime(
                    node['createdAt'], "%Y-%m-%dT%X.%fZ").astimezone(UTC()) < datetime.strptime(
                    first_node['createdAt'], "%Y-%m-%dT%X.%fZ").astimezone(UTC()):
                end, record_count = proc_node(first_node,
                                              path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)
                first_node_inserted = True
                if end == True:
                    break

            # TODO: rewrite proc_node and make those function call more clean and effective
            #       justice if need to process this node then call "proc_node"
            end, record_count = proc_node(node,
                                          path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit)
            if end == True:
                break

        if end == True or loadMoreKey == None:
            break

    if add_data == True:

        with open(origin_path, 'r', encoding='utf-8') as ori_f:
            with open(path, 'a', encoding='utf-8') as new_f:
                new_f.write(ori_f.read())

        os.remove(origin_path)
        os.rename(path, origin_path)

    done(request_count, "request(s) sent.")
    done(record_count, "record(s) saved.")


def crawl_collections(user_id, path, mode="a", b_save_pics=False, record_count_limit=None, start_time=BASE_TIME, end_time=datetime.now(GMT8()), update=True) -> None:
    ...


def crawl_profile() -> None:
    ...


def crawl_following(user_id: str, path: str = os.path.join(DIR_PATH, "data/relation/following.json")) -> None:

    crawl_relation(user_id, path, API_GET_FOLLOWING_LIST)


def crawl_follower(user_id: str, path: str = os.path.join(DIR_PATH, "data/relation/follower.json")) -> None:

    crawl_relation(user_id, path, API_GET_FOLLOWER_LIST)


def crawl_relation(user_id: str, path: str, api: str) -> None:

    debug(os.path.abspath(os.path.join(path, os.path.pardir)))
    os.remove(path) if os.path.isfile(path) else os.makedirs(
        os.path.abspath(os.path.join(path, os.path.pardir)), exist_ok=True)
    # info("Old data has been removed.")

    payload_relation = {
        "limit": 200,
        "username": user_id,
        "loadMoreKey": ""
    }

    request_count = 0
    record_count = 0
    users = []

    while True:
        request_count += 1
        info("sending request", request_count)

        if request_count > 1:
            payload_relation["loadMoreKey"] = response.json()["loadMoreKey"]

        response = call_api(api, payload_relation)

        for node in response.json()["data"]:
            del node["decorations"]
            del node["avatarImage"]
            # save_json(node, path, "a")
            users.append(node)
            record_count += 1

        if "loadMoreKey" not in response.json():
            break

    save_json_list(users, path)

    done(request_count, "request(s) sent.")
    done(record_count, "record(s) saved.")


def get_mutual_following_list():
    follower_list = read_multi_json_file(
        os.path.join(DIR_PATH, "data/relation/follower.json"))
    following_list = read_multi_json_file(
        os.path.join(DIR_PATH, "data/relation/following.json"))

    mutual_list = mutually_following(follower_list, following_list)
    one_way_following_list = one_way_following(follower_list, following_list)
    one_way_follower_list = one_way_follower(follower_list)

    done("Mutually following with", len(mutual_list), "user(s).")

    save_json_list(mutual_list, os.path.join(
        DIR_PATH, "data/relation/nutually_following.json"))
    save_json_list(one_way_following_list, os.path.join(
        DIR_PATH, "data/relation/one_way_following_list.json"))
    save_json_list(one_way_follower_list, os.path.join(
        DIR_PATH, "data/relation/one_way_follower_list.json"))


if __name__ == "__main__":
    CURR_TIME = datetime.now(GMT8())
    noti_path = os.path.join(DIR_PATH, "data/notifications.json")
    post_path = os.path.join(DIR_PATH, "data/posts.json")

    ##################################################
    # ATTENTION: Replace with your own Jike user id. #
    user_id = "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
    ##################################################

    b_save_pics = True  # Bool

    # operate posts created during 2021/12/01 and 2021/12/31
    # class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
    # start_time = datetime(2021, 1, 1, tzinfo=GMT8())
    # end_time = datetime(2021, 1, 10, tzinfo=GMT8())

    # operate posts created before 30 days ago
    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # time_delta = timedelta(days=30)
    # end_time = CURR_TIME - time_delta

    noti_start_time = BASE_TIME  # datetime
    noti_end_time = CURR_TIME   # datetime
    noti_record_limit = None    # int or None

    # crawl_notifications(noti_path, "a", False,
    #                     noti_record_limit, noti_start_time, noti_end_time)

    post_start_time = BASE_TIME  # datetime
    post_end_time = CURR_TIME   # datetime
    post_record_limit = None    # int or None

    sort_nodes(post_path)

    crawl_posts(user_id, post_path, "a", b_save_pics,
                post_record_limit, post_start_time, post_end_time)

    # crawl_following(user_id)
    # crawl_follower(user_id)
    # get_mutual_following_list()
