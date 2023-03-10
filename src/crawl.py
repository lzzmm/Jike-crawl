# -*- coding:utf8 -*-
# create at: 2023-01-15T09:33:25Z+08:00
# author:    lzzmm<2313681700@qq.com>
# comment:   This file is a mount of shit and need to be rewritten

import os
import sys
import json
import requests
from datetime import datetime

from utils import *
from common import *


DIR_PATH = os.path.dirname(os.path.dirname(__file__))


def proc_node(node, path, mode, start_time, end_time, end, record_count, b_save_pics=False, record_count_limit=None, pic_path="data/pics/"):
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
        if "video" in node and node["video"] is not None:
            node["video"]["url"] = get_media_url(node["id"], node["type"])
        save_json(node, path, mode)
        if b_save_pics and ("pictures" in node) and len(node["pictures"]) != 0:
            save_pics(node, pic_path)
            
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

    info("Running crawl_notifications.")

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
                node = json.loads(line)
                if 'createdAt' in node:
                    start_time = datetime.strptime(
                        node['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
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
    loop and crawl all posts and save into database/file
    TODO: function too long! rewrite it!
    ---
    args:
    - path: file path 
    - user_id: Jike user id
    - num: number of records to crawl
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """

    info("Running crawl_posts.")
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
                node = json.loads(line)
                if 'createdAt' in node:
                    start_time = datetime.strptime(
                        node['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
                    info("Read record(s) from", start_time)
                    path = os.path.join(
                        DIR_PATH, "data/temp-new-data-posts.json")
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
                                              path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit,
                                              "data/pics/posts/")
                first_node_inserted = True
                if end == True:
                    break

            # TODO: rewrite proc_node and make those function call more clean and effective
            #       justice if need to process this node then call "proc_node"
            end, record_count = proc_node(node,
                                          path, mode, start_time, end_time, end, record_count, b_save_pics, record_count_limit,
                                          "data/pics/posts/")
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


def crawl_comment(m_id: str, m_type: str, b_save_pics: bool = False, b_update_comments: bool = False, path: str = None, pic_path: str = "data/pics/comments") -> None:

    info("%s: %s" % (m_type, m_id))

    if path is None:
        path = os.path.join(DIR_PATH, "data/comments/")
        os.makedirs(path) if not os.path.isdir(path) else ...
        path = os.path.join(path, m_id + ".json")
        if os.path.isfile(path):
            info("comment file already exists.")
            if b_update_comments == True:
                os.remove(path)
            else:
                return
    else:
        # path=os.join(DIR_PATH, path)
        ...

    payload = PAYLOAD_MESSAGE_COMMENTS
    payload["variables"] = {
        "messageId": m_id,
        "messageType": m_type
    }

    payload_sub_comments = PAYLOAD_SUB_COMMENTS

    # b_has_comments = False
    request_count = 0
    # record_count = 0

    while True:

        response = crawl(API_GRAPHQL, COOKIES, HEADERS, payload)
        request_count += 1

        loadMoreKey = response.json(
        )["data"]["message"]["comments"]["pageInfo"]["loadMoreKey"]
        # important, loadMoreCommentKey not loadMoreKey
        payload["variables"]["loadMoreCommentKey"] = loadMoreKey
        info("sending request", request_count, loadMoreKey)

        for node in response.json()["data"]["message"]["comments"]["nodes"]:

            if node["replyCount"] > len(node["hotReplies"]):
                payload_sub_comments["variables"]["targetType"] = node["targetType"]
                payload_sub_comments["variables"]["commentId"] = node["id"]

                response_sub_comments = crawl(
                    API_GRAPHQL, COOKIES, HEADERS, payload_sub_comments)

                node["hotReplies"] = response_sub_comments.json()["data"]["commentDetail"]["listSubComments"]
                # info(node["hotReplies"])

            save_json(node, path, "a")

            # record_count += 1

            if b_save_pics:
                ...
                if "pictures" in node and len(node["pictures"]) != 0:
                    save_pics(node, pic_path)

                if node["hotReplies"] is not None and len(node["hotReplies"]) != 0:
                    for hot_reply in node["hotReplies"]:
                        if "pictures" in hot_reply and len(hot_reply["pictures"]) != 0:
                            save_pics(hot_reply, pic_path)

        if loadMoreKey == None:
            break

    # if b_has_comments == True:
    #     done("%s: %s" % (m_type, m_id), "comment(s) saved.")
    # else:
    #     done("%s: %s" % (m_type, m_id), "no comment to be saved.")


def crawl_comments(posts_path: str, b_save_pics: bool = False, b_update_comments: bool = False, record_count_limit: int = None, path: str = None) -> None:
    """
    Read from posts.json and get id and type, then crawl comments base on them
    ---

    """
    info("Running crawl_comments.")

    record_count = 0
    m_list = [[node["id"], node["type"]]
              for node in read_multi_json_file(posts_path, record_count_limit) if node["commentCount"] > 0]

    list_len = len(m_list)
    for idx, msg in enumerate(m_list):
        
        crawl_comment(msg[0], msg[1], b_save_pics, b_update_comments)
        record_count += 1
        done("%d/%d %s: %s" %
             (idx + 1, list_len, msg[1], msg[0]), "comment(s) saved.")

    done(record_count, "post(s) operated.")


def crawl_collections(path, mode="a", b_save_pics=False, record_count_limit: int = None, update=True) -> None:
    """
    loop and crawl all collections and save into database/file
    TODO: function too long! rewrite it!
    ---
    args:
    - path: file path 
    - user_id: Jike user id
    - num: number of records to crawl
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """
    global CURR_TIME

    CURR_TIME = datetime.now(GMT8())  # current time

    info("Running crawl_collections.")

    payload = PAYLOAD_USER_COLLECTIONS
    # payload["variables"]["username"] = user_id

    end = False
    add_data = False
    request_count = 0
    record_count = 0
    origin_path = path
    start_id = ""

    if update == True:
        try:
            with open(path, 'r', encoding="utf8") as f:
                line = f.readline()
                node = json.loads(line)
                if 'id' in node:
                    start_id = node['id']
                    info("Read record(s) from", start_id)
                    path = os.path.join(
                        DIR_PATH, "data/temp-new-data-collections.json")
                    os.remove(path) if os.path.isfile(path) else ...
                    add_data = True
        except Exception as e:
            warn(e.args)

    while True:

        response = crawl(API_GRAPHQL, COOKIES, HEADERS, payload)
        request_count += 1

        loadMoreKey = response.json()[
            "data"]["viewer"]["collections"]["pageInfo"]["loadMoreKey"]
        payload["variables"]["loadMoreKey"] = loadMoreKey
        info("sending request", request_count, loadMoreKey)

        for node in response.json()["data"]["viewer"]["collections"]["nodes"]:

            if node["id"] == start_id:
                end = True
                break

            # TODO: rewrite proc_node and make those function call more clean and effective
            #       justice if need to process this node then call "proc_node"
            end, record_count = proc_node(node,
                                          path, mode, BASE_TIME, CURR_TIME, end, record_count, b_save_pics, record_count_limit, "data/pics/collections/")
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


def crawl_following(user_id: str, path: str = os.path.join(DIR_PATH, "data/relation/following.json")) -> None:

    crawl_relation(user_id, path, API_GET_FOLLOWING_LIST)


def crawl_follower(user_id: str, path: str = os.path.join(DIR_PATH, "data/relation/follower.json")) -> None:

    crawl_relation(user_id, path, API_GET_FOLLOWER_LIST)


def crawl_relation(user_id: str, path: str, api: str) -> None:

    info("Running crawl_relation.")

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

        response = call_api_post(api, payload_relation)

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


def crawl_profile(user_id: str) -> None:

    info("Running crawl_profile.")

    api = API_USER_PROFILE + "?username=" + user_id
    payload = {"username": user_id}

    response = call_api_get(api, payload)

    info(response)
    
    user = response.json()["user"]
    
    path = os.path.join(DIR_PATH, "data/profiles/" +
                        user["username"] + "-profile.json")

    save_json(user, path, "w", 2)
    
    report_data_path = os.path.join(DIR_PATH, "data/report_data.json")
    
    json_data = read_json_file(report_data_path)
    
    json_data['username'] = user['screenName']
    json_data['uuid'] = user['username']
    
    create_time = datetime.strptime(
        user['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
    time_delta = CURR_TIME - create_time
    json_data['total_days'] = time_delta.days
    
    save_json(json_data, report_data_path, 'w', 2)

    done("Data saved into", path)


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
    coll_path = os.path.join(DIR_PATH, "data/collections.json")

    ##################################################
    # ATTENTION: Replace with your own Jike user id. #
    user_id = "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
    ##################################################

    b_save_pics = False  # Bool
    b_save_coll_pics = False  # Bool

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

    crawl_notifications(noti_path, "a", False,
                        noti_record_limit, noti_start_time, noti_end_time)

    post_start_time = BASE_TIME  # datetime
    post_end_time = CURR_TIME   # datetime
    post_record_limit = None    # int or None

    sort_nodes(post_path)

    crawl_posts(user_id, post_path, "a", b_save_pics,
                post_record_limit, post_start_time, post_end_time)
    crawl_comments(post_path)

    # crawl_following(user_id)
    # crawl_follower(user_id)
    # get_mutual_following_list()

    coll_record_limit = None

    crawl_collections(coll_path, "a", b_save_coll_pics, coll_record_limit)
    crawl_comments(coll_path)

    crawl_profile(user_id)
