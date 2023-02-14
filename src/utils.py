# -*- coding:utf8 -*-
# create at: 2023-01-15T23:26:10Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo

from config import *
from common import *


def refresh_cookies():

    warn("accessToken expired, trying to refresh accessToken...")

    try:
        response = requests.post(API_GRAPHQL, cookies=COOKIES,
                                 headers=HEADERS,
                                 data=json.dumps(PAYLOAD_REFRESH_COOKIES))
        debug(response)

    except requests.exceptions.ConnectionError as e:
        err("Connection error", e.args)

    if 'errors' in response.json() and response.json()["errors"][0]["extensions"]["code"] == "UNAUTHENTICATED":
        err("Please copy latest cookie from DevTools of browser to ./config/cookies.txt!")
        sys.exit(1)

    accessToken = response.json()["data"]["refreshToken"]["accessToken"]
    refreshToken = response.json()["data"]["refreshToken"]["refreshToken"]
    COOKIES['cookie'] = '_ga=GA1.2.1010923813.1673409584; _gid=GA1.2.564544936.1673409584; fetchRankedUpdate=1673538878642; x-jike-access-token=' + \
        accessToken + '; x-jike-refresh-token=' + refreshToken

    # Write cookie in file
    with open(os.path.join(DIR_PATH, 'config/cookies.txt'), 'w', encoding="utf8") as f:
        f.write(COOKIES['cookie'])
        done("Token updated.")


def get_access_token(path: str = os.path.join(DIR_PATH, 'config/cookies.txt')) -> str:
    """    
    Return:
        str, x-jike-access-token
    """
    return open(path).read().split(sep="x-jike-access-token=")[1].split(sep="; x-jike-refresh-token=")[0]


def get_refresh_token(path: str = os.path.join(DIR_PATH, 'config/cookies.txt')) -> str:
    """
    Return:
        str, x-jike-refresh-token
    """
    return open(path).read().split(sep="x-jike-access-token=")[1].split(sep="x-jike-refresh-token=")[1]


def handle_errors(response, halt=True) -> None:
    """
    handle http errors
    ---
    args:
    - response: the http response
    - halt: bool, if true, stop program when unexpected error occurs
    """
    warn(response.json()["errors"][0]["extensions"]["code"])
    debug(response.json())

    if response.json()["errors"][0]["extensions"]["code"] == "UNAUTHENTICATED":
        refresh_cookies()
    else:
        err("Unexpected error: ", response.json()["errors"][0]["extensions"])
        if halt:
            sys.exit(1)


def crawl(url, cookies, headers, payload) -> requests.Response:
    """
    crawl data TODO: Could be replaced by "op_post"
    ---
    args: 
    - url
    - cookies
    - headers
    - payload
    - return: response
    """
    try:
        response = requests.post(url, cookies=cookies,
                                 headers=headers,
                                 data=json.dumps(payload))

    except requests.exceptions.ConnectionError as e:
        err("Connection error", e.args)

    # The "has_key" method has been removed in Python 3
    # TODO: Needs to improve here
    try:
        if 'errors' in response.json():

            handle_errors(response)
            # must use new COOKIES here
            response = crawl(url, COOKIES, headers, payload)

    except json.JSONDecodeError or UnboundLocalError as e:
        err(e.args)

    return response


# haven't finished yet, but works well
def crawl_posts_fn(user_id: str, proc_node_fn, op_payload=None, miss_feed_only: bool = False, user_id_list: list = None, record_count_limit=None, start_time=BASE_TIME, end_time=datetime.now(GMT8()), update=False) -> list:
    """
    loop and crawl posts from user_id and do something TODO: rewrite, and some bugs are still remaining, do fn after crawled, don't want to reconstruct it because it is a mount of shit
    ---
    args:
    - user_id: Jike user id
    - proc_node_fn: function to process the crawled post
    - op_payload: payload for function op which is called in proc_node_fn
    - miss_feed_only: whether only check miss feed
    - record_count_limit: number of records to crawl, default no limit
    - start_time: datetime object
    - end_time: datetime object, later than start_time
    """
    debug("running crawl_posts_fn", user_id, miss_feed_only, user_id_list)

    payload = PAYLOAD_FETCH_SELF_FEEDS
    if miss_feed_only != True:
        payload = PAYLOAD_USER_FEEDS
        payload["variables"]["username"] = user_id

    end = False
    add_data = False
    is_first_node = True
    first_node_inserted = False
    request_count = 0
    record_count = 0
    first_node = {}
    res_nodes = []
    payload["variables"]["loadMoreKey"] = None  # need to re-initialize

    while True:  # pseudo-do-while in python

        debug(payload["variables"])

        response = crawl(API_GRAPHQL, COOKIES, HEADERS, payload)
        request_count += 1

        if miss_feed_only == False:
            viewer = "userProfile"
            feeds = "feeds"
        else:
            viewer = "viewer"
            feeds = "followingUpdates"

        try:
            loadMoreKey = response.json()[
                "data"][viewer][feeds]["pageInfo"]["loadMoreKey"]
            payload["variables"]["loadMoreKey"] = loadMoreKey

        except TypeError as e:
            err(e.args)
        debug("sending request", request_count, loadMoreKey)

        for node in response.json()["data"][viewer][feeds]["nodes"]:

            debug(node)
            if node["type"] != "ORIGINAL_POST" and node["type"] != "REPOST":
                continue

            if miss_feed_only == True and ("user" in node and node["user"]["username"] not in user_id_list):
                continue

            if miss_feed_only != True and ("user" in node and node["user"]["username"] != user_id):
                continue

            end, record_count = proc_node_fn(
                node, end, record_count, op_post, op_payload, start_time, end_time, record_count_limit)

            res_nodes.append(node)

            if end == True:
                break

        if end == True or loadMoreKey == None or (miss_feed_only == True and loadMoreKey["lastPageEarliestTime"] < loadMoreKey["lastReadTime"]):
            break

    done(request_count, "request(s) sent.")
    done(record_count, "record(s) operated.")

    return res_nodes


def proc_node_fn(node, end, record_count, op, op_payload=None, start_time=BASE_TIME, end_time=CURR_TIME, record_count_limit=None) -> list:
    """
    process notification/post TODO: rewrite
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

    if time > start_time and time <= end_time:
        op_payload["variables"]["id"] = node["id"]
        op_payload["variables"]["messageType"] = node["type"]
        op(op_payload)
        done(node["content"], time.astimezone(GMT8()))
        record_count += 1

    if (record_count_limit != None and record_count >= record_count_limit) or (time < start_time):
        end = True

    return end, record_count


def get_user_id(user_name: str) -> str:
    """
    Get user_id("userName" in remote db) by user_name("screenName" in remote db)
    ---
    args:
    - user_name: user screen name, str

    return: user id, str
    """

    PAYLOAD_RELATED_KEYWORDS["variables"]["keywords"] = user_name
    PAYLOAD_SEARCH_INTEGRATE["variables"]["keywords"] = user_name

    try:
        response = op_post(PAYLOAD_RELATED_KEYWORDS)
        # debug(response.json())

        for tip in response.json()["data"]["search"]["relatedKeywordTips"]:

            if tip["type"] == "user":
                return tip["url"].lstrip("/u")

        response = op_post(PAYLOAD_SEARCH_INTEGRATE)
        # debug(response.json())

        for node in response.json()["data"]["search"]["integrate"]["nodes"]:

            if "items" in node:
                return node["items"][0]["username"]

    except Exception as e:
        err("In get_user_id!", e.args)


def call_api(api, payload) -> requests.Response:
    """
    call api
    ---
    args:
    """

    # refresh_cookies()

    headers = HEADERS
    headers["referer"] = "https://web.okjike.com/"
    headers["x-jike-access-token"] = get_access_token()
    headers["x-jike-refresh-token"] = get_refresh_token()

    try:
        response = op_post(payload, api, headers)
        # debug(response, response.json())
        return response

    except Exception as e:
        err("In call_api", e.args)


def op_post(payload, url=API_GRAPHQL, headers=HEADERS, cookies=COOKIES) -> requests.Response:  # 这四个作为一个类
    """
    post with payload
    """
    # TODO: optimize code structure

    assert payload is not None

    try:
        response = requests.post(url, cookies=cookies,
                                 headers=headers,
                                 data=json.dumps(payload))

    except requests.exceptions.ConnectionError as e:
        err("Connection error", e.args)

    try:
        if 'errors' in response.json():

            handle_errors(response, halt=False)
            response = op_post(payload)

    except Exception as e:
        err(e.args)

    return response


def update_user_id_list() -> list:
    """
    update "config/user_id_list.txt"
    base on "config/user_name_list.txt"
    ---
    return:
        user_id_list
    """

    user_name_list = read_list_file(os.path.join(
        DIR_PATH, "config/user_name_list.txt"))

    user_id_list = []

    for user_name in user_name_list:

        user_id = get_user_id(user_name)
        user_id_list.append(user_id)
        info(user_name, user_id)

    save_list(user_id_list, os.path.join(DIR_PATH, "config/user_id_list.txt"))

    done(len(user_id_list), "line(s) operated.")

    return user_id_list


def mutually_following(follower_list: list, following_list: list) -> list:
    # list1 = follower_list if len(follower_list) > len(following_list) else following_list # greater
    # list2 = following_list if len(follower_list) > len(following_list) else follower_list
    list_res = []

    for user in follower_list:
        for item in following_list:
            if user["id"] == item["id"]:
                list_res.append(user)

    return list_res


def one_way_follower(follower_list: list) -> list:

    return [user for user in follower_list if user["following"] == False]


def one_way_following(follower_list: list, following_list: list) -> list:

    list_res = []

    for user in following_list:
        exist = False
        for item in follower_list:
            if user["id"] == item["id"]:
                exist = True
                break
        if not exist:
            list_res.append(user)

    return list_res


def sort_nodes(path) -> None:
    """
    Sort nodes in time order, from later to earlier
    ---
    args:
    - path: path to json file
    """
    try:
        nodes = read_multi_json_file(path)

        nodes.sort(key=lambda x: x['createdAt'],  reverse=True)

        with open(path, "w", encoding="utf8") as f:
            for node in nodes:
                save_json(node, path, "a")

        done("Sorted.")
    except Exception:
        warn("Not sorted.")


#####################################
#   print functions                 #
#####################################
def print_colored(fmt: str, *args, color="default") -> None:
    ...


#####################################
#   logger                          #
#####################################
def debug(*values: object, b_log=True) -> None:
    if PRINT_LEVEL < 1:
        print("\033[34m[DEBUG]", *values, "\033[0m")
    if LOG_LEVEL < 1 and b_log == True:
        log("[DEBUG]", *values)


def info(*values: object, b_log=True) -> None:
    if PRINT_LEVEL < 2:
        print("\033[36m[INFO]", *values, "\033[0m")
    if LOG_LEVEL < 2 and b_log == True:
        log("[INFO]", *values)


def done(*values: object, b_log=True) -> None:
    if PRINT_LEVEL < 3:
        print("\033[32m[DONE]", *values, "\033[0m")
    if LOG_LEVEL < 3 and b_log == True:
        log("[DONE]", *values)


def warn(*values: object, b_log=True) -> None:
    if PRINT_LEVEL < 4:
        print("\033[35m[WARN]", *values, "\033[0m")
    if LOG_LEVEL < 4 and b_log == True:
        log("[WARN]", *values)


def err(*values: object, b_log=True) -> None:
    if PRINT_LEVEL < 5:
        print("\033[31m[ERROR]", *values, "\033[0m", file=sys.stderr)
    if LOG_LEVEL < 5 and b_log == True:
        log("[ERROR]", *values)


def crit(*values: object, b_log=True) -> None:
    if PRINT_LEVEL < 6:
        print("\033[33m[CRITICAL]", *values, "\033[0m", file=sys.stderr)
    if LOG_LEVEL < 6 and b_log == True:
        log("[CRITICAL]", *values)


#####################################
#   read file                       #
#####################################
def read_multi_json_file(path, lines=None) -> list:
    """
    Read multi-object json file
    ---
    args:
    - path: path to json file
    - lines: lines to read

    return: json object list
    """

    x = []

    if not os.path.isfile(path):
        err("File not found: %s" % path)
        return x

    try:
        with open(path, 'r', encoding="utf8") as f:
            count = 0
            line = f.readline()

            while line and (lines == None or count < lines):
                x.append(json.loads(line))
                count += 1
                line = f.readline()

            done("Read", count, "line(s) from", path)

    except Exception as e:
        err("Failed reading file.", e.args)

    return x


def read_list_file(path, lines=None) -> list:
    """
    Read list file
    ---
    args:
    - path: path to file
    - lines: lines to read

    return: list
    """

    x = []

    if not os.path.isfile(path):
        err("File not found: %s" % path)
        return x

    try:
        with open(path, 'r', encoding="utf8") as f:
            count = 0
            line = f.readline()

            while line and (lines == None or count < lines):
                # important to remove trailing "\n"
                x.append(line.rstrip("\n"))
                count += 1
                line = f.readline()

            done("Read", count, "line(s) from", path)

    except Exception as e:
        err("Failed reading file.", e.args)

    return x


def read_file(path) -> str:
    ...


#####################################
#  write file                       #
#####################################
def log(*values: object, path: str = "data/logs/log.txt") -> None:

    CURR_TIME = datetime.now(GMT8())

    try:
        with open(os.path.join(DIR_PATH, path), 'a', encoding='utf-8') as f:

            print(CURR_TIME.__format__("%Y-%m-%d %X %Z"), *values, file=f)

    except Exception as e:
        err(e.args)


def clear_log(path: str = "data/logs/log.txt"):
    try:
        path = os.path.join(DIR_PATH, path)
        os.remove(path) if os.path.isfile(path) else ...

    except Exception as e:
        err(e.args)

    done("data/logs/log.txt has been cleared.")


def save_list(list: list, path: str, mode="w") -> None:
    """
    Save a list of lines into a file
    """

    with open(path, mode, encoding="utf8") as f:

        for line in list:
            f.write(line)
            f.write("\n")

    done("List saved at", path)


def save_pics(node) -> None:
    """
    save pictures in post
    ---
    args:
    - node: json object with a list of pictures info to save
    """

    pic_path = os.path.join(DIR_PATH, "data/pics/", node["id"])
    os.makedirs(pic_path, exist_ok=True)

    for pic in node["pictures"]:
        picUrl = pic["picUrl"]
        response = requests.get(picUrl)
        # count += 1
        # with open (os.path.join(pic_path, str(count)), 'wb') as f:
        with open(os.path.join(pic_path, picUrl.split("?")[0].split("/")[-1]), 'wb') as f:
            f.write(response.content)

    done("Pictures saved at", pic_path)


def save_json(node, path, mode, indent=None) -> None:
    """
    save json object into json file
    ---
    args: 
    - node: json object
    - path: json file path
    - mode: "a" for add, "w" for overwrite
    - indent: int, default: None
    """
    with open(path, mode, encoding="utf8") as f:
        json.dump(node, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def save_json_list(list: list, path: str) -> None:
    """
    Save a list of json objects into a file
    """
    debug("save_json_list", os.path.abspath(
        os.path.join(path, os.path.pardir)))
    os.remove(path) if os.path.isfile(path) else os.makedirs(
        os.path.abspath(os.path.join(path, os.path.pardir)), exist_ok=True)

    for obj in list:
        save_json(obj, path, "a", indent=None)

    done("Json object list saved at", path)


# Functions NOT used yet...
def save_db(node) -> None:
    """
    store data into mysql
    ---
    args: 
    - node: json object
    """
    # TODO: store into db
    debug(node)


def save_csv(node, path) -> None:
    """
    store data into csv
    ---
    args: 
    - node: json object
    - path: csv file path
    """
    # TODO: store into csv
    debug(node)


def print_format(str, way, width, fill=' ', ed='') -> None:
    try:
        count = 0
        for word in str:
            if (word >= '\u4e00' and word <= '\u9fa5') or word in ['，', '。', '、', '？', '；', '：', '【', '】', '（', '）', '……', '——', '《', '》']:
                count += 1
        width -= count if width >= count else 0
        print('{0,:{1}{2}{3}}'.format(
            str, fill, way, width), end=ed, flush=True)
    except:
        err("Error occurs in print_format()")
