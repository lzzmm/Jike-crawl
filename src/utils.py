# -*- coding:utf8 -*-
# create at: 2023-01-15T23:26:10Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo


ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return ZERO

    def fromutc(self, dt):
        return dt


class GMT8(tzinfo):
    def utcoffset(self, dt):
        return HOUR * 8

    def tzname(self, dt):
        return 'GMT+8'

    def dst(self, dt):
        return ZERO

    def fromutc(self, dt):
        return dt + dt.utcoffset()


BASE_TIME = datetime(2015, 3, 28, tzinfo=GMT8())  # Jike 1.0 online
CURR_TIME = datetime.now(GMT8())  # current time


dir_path = os.path.dirname(os.path.dirname(__file__))

url = "https://web-api.okjike.com/api/graphql"

headers = {
    'content-type': 'application/json',
    'origin': 'https://web.okjike.com',
    'sec-ch-ua-platform': '"Windows"',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

cookies = {
    'cookie': open(os.path.join(dir_path, 'cfgfiles/cookies.txt')).read()
}


def refresh_cookies():
    print("accessToken expired, trying to refresh accessToken...")

    payload = {
        "operationName": "refreshToken",
        "variables": {},
        "query": "mutation refreshToken {\n  refreshToken {\n    accessToken\n    refreshToken\n  }\n}\n"
    }

    try:
        x = requests.post(url, cookies=cookies,
                          headers=headers,
                          data=json.dumps(payload))
        print(x)
    except requests.exceptions.ConnectionError as e:
        print("Connection error", e.args)

    if 'errors' in x.json() and x.json()["errors"][0]["extensions"]["code"] == "UNAUTHENTICATED":
        print(
            "Please copy latest cookie from DevTools of browser to ./cfgfiles/cookies.txt!")
        sys.exit(1)

    accessToken = x.json()["data"]["refreshToken"]["accessToken"]
    refreshToken = x.json()["data"]["refreshToken"]["refreshToken"]
    cookies['cookie'] = '_ga=GA1.2.1010923813.1673409584; _gid=GA1.2.564544936.1673409584; fetchRankedUpdate=1673538878642; x-jike-access-token=' + \
        accessToken + '; x-jike-refresh-token=' + refreshToken

    # Write cookie in file
    with open(os.path.join(dir_path, 'cfgfiles/cookies.txt'), 'w', encoding="utf8") as f:
        f.write(cookies['cookie'])
        print("Token updated.")


def handle_errors(x, halt=True):
    """
    handle http errors
    ---
    args:
    - x: the http response
    - halt: bool, if true, stop program when unexpected error occurs
    """
    print(x.json()["errors"][0]["extensions"]["code"])

    if x.json()["errors"][0]["extensions"]["code"] == "UNAUTHENTICATED":
        refresh_cookies()
    else:
        print("Unexpected error: ", x.json()["errors"][0]["extensions"])
        if halt:
            sys.exit(1)


def crawl(url, cookies, headers, payload):
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
        x = requests.post(url, cookies=cookies,
                          headers=headers,
                          data=json.dumps(payload))
        print(x)
    except requests.exceptions.ConnectionError as e:
        print("Connection error", e.args)

    # The "has_key" method has been removed in Python 3
    # TODO: Needs to improve here
    if 'errors' in x.json():
        handle_errors(x)
        x = crawl(url, cookies, headers, payload)

    return x


# haven't finished yet, but works well
def crawl_posts_fn(user_id, proc_node_fn, op_payload=None, miss_feed_only=False, record_count_limit=None, start_time=BASE_TIME, end_time=CURR_TIME, update=False):
    """
    loop and crawl posts from user_id and do something TODO: rewrite, and some bugs are still remaining
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

    payload = {
        "operationName": "UserFeeds",
        "query": open(os.path.join(dir_path, "query/query_user_feeds.txt")).read(),
        "variables": {
            "username": user_id
        }
    }

    if miss_feed_only == True:
        payload = {
            "operationName": "MissedFeeds",
            "query": open(os.path.join(dir_path, "query/query_miss_feeds_original.txt")).read(),
            "variables": {}
        }

    end = False
    add_data = False
    is_first_node = True
    first_node_inserted = False
    request_count = 0
    record_count = 0
    first_node = {}

    while True:  # pseudo-do-while in python

        x = crawl(url, cookies, headers, payload)
        request_count += 1

        if miss_feed_only == False:
            viewer = "userProfile"
            feeds = "feeds"
        else:
            viewer = "viewer"
            feeds = "missedFeeds"

        loadMoreKey = x.json()[
            "data"][viewer][feeds]["pageInfo"]["loadMoreKey"]
        payload["variables"]["loadMoreKey"] = loadMoreKey
        print(request_count, loadMoreKey)

        for node in x.json()["data"][viewer][feeds]["nodes"]:

            print(node)
            # not tested yet
            if miss_feed_only == True and node["user"]["username"] != user_id:
                print(node["user"]["username"])
                continue

            end, record_count = proc_node_fn(
                node, end, record_count, op_post, op_payload, start_time, end_time, record_count_limit)

            if end == True:
                break

        if end == True or loadMoreKey == None:
            break

    print(request_count, "request(s) was(were) sent.")
    print(record_count, "record(s) operated.")


def proc_node_fn(node, end, record_count, op, op_payload=None, start_time=BASE_TIME, end_time=CURR_TIME, record_count_limit=None):
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

    if time >= start_time and time <= end_time:
        op_payload["variables"]["id"] = node["id"]
        op(op_payload)
        print(node["content"], "\n", time, "\n", sep="")
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

    payload_releated_keywords = {
        "operationName": "SearchReleatedKeywords",
        "variables": {
            "keywords": user_name
        },
        "query": "query SearchReleatedKeywords($keywords: String!) {\n  search {\n    relatedKeywordTips(keywords: $keywords) {\n      type\n      description\n      icon\n      suggestion\n      url\n      __typename\n    }\n    __typename\n  }\n}\n"
    }

    payload_search_integrate = {
        "operationName": "SearchIntegrate",
        "variables": {
            "keywords": user_name
        },
        "query": open(os.path.join(dir_path, "query/query_search_integrate.txt")).read()
    }

    try:
        x = op_post(payload_releated_keywords)
        # print(x.json())

        for tip in x.json()["data"]["search"]["relatedKeywordTips"]:

            if tip["type"] == "user":
                return tip["url"].lstrip("/u")

        x = op_post(payload_search_integrate)
        # print(x.json())

        for node in x.json()["data"]["search"]["integrate"]["nodes"]:

            if "items" in node:
                return node["items"][0]["username"]

    except Exception:
        print("Exception in get_user_id!")


def op_post(payload, url=url, headers=headers, cookies=cookies):
    """
    post with payload
    """
    # TODO: optimize code structure

    assert payload is not None

    try:
        x = requests.post(url, cookies=cookies,
                          headers=headers,
                          data=json.dumps(payload))
        # print(x, x.json())
    except requests.exceptions.ConnectionError as e:
        print("Connection error", e.args)

    if 'errors' in x.json():
        # FIXME: JSONDecodeError("Expecting value", s, err.value) from None
        handle_errors(x, halt=False)
        x = op_post(payload)

    return x


def update_user_id_list() -> list:
    """
    update "cfgfiles/user_id_list.txt"
    base on "cfgfiles/user_name_list.txt"
    ---
    return:
        user_id_list
    """

    user_name_list = read_list_file(os.path.join(
        dir_path, "cfgfiles/user_name_list.txt"))

    user_id_list = []

    for user_name in user_name_list:

        user_id = get_user_id(user_name)
        user_id_list.append(user_id)
        print(user_name, user_id)

    save_list(user_id_list, os.path.join(
        dir_path, "cfgfiles/user_id_list.txt"))

    print(len(user_id_list), "line(s) operated.")

    return user_id_list


def sort_nodes(path):
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

        print("Sorted.")
    except Exception:
        print("Not sorted.")


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
    try:
        with open(path, 'r', encoding="utf8") as f:
            count = 0
            line = f.readline()

            while line and (lines == None or count < lines):
                x.append(json.loads(line))
                count += 1
                line = f.readline()

            print("Read", count, "line(s) from", path)

    except Exception:
        print("Failed reading file.")

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
    try:
        with open(path, 'r', encoding="utf8") as f:
            count = 0
            line = f.readline()

            while line and (lines == None or count < lines):
                # important to remove trailing "\n"
                x.append(line.rstrip("\n"))
                count += 1
                line = f.readline()

            print("Read", count, "line(s) from", path)

    except Exception:
        print("Failed reading file.")

    return x


#####################################
#  write file                       #
#####################################
def save_list(list: list, path: str, mode="w"):
    """
    Save a list of lines into a file
    """

    with open(path, mode, encoding="utf8") as f:

        for line in list:
            f.write(line)
            f.write("\n")


def save_pics(node):
    """
    save pictures in post
    ---
    args:
    - node: json object with a list of pictures info to save
    """

    pic_path = os.path.join(dir_path, "data/pics/", node["id"])
    os.makedirs(pic_path, exist_ok=True)

    for pic in node["pictures"]:
        picUrl = pic["picUrl"]
        x = requests.get(picUrl)
        # count += 1
        # with open (os.path.join(pic_path, str(count)), 'wb') as f:
        with open(os.path.join(pic_path, picUrl.split("?")[0].split("/")[-1]), 'wb') as f:
            f.write(x.content)

    print("Pictures saved at", pic_path)


def save_json(node, path, mode, indent=None):
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


# Functions NOT used yet...
def crawl_following() -> None:
    """
    get following users
    TBD
    ---
    args:
    """

    # url = "https://api.ruguoapp.com/1.0/userRelation/getFollowerList"

    payload = {
        # TODO: could not find a graphql API
        # "operationName": "ListFollower",
        # "variables": {
        #     "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
        # },
        # "query": "query ListFollower {\n followedCount \n__typename\n}\n"
        # "limit": 20,
        # "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
    }

    # try:
    x = op_post(payload)
    print(x, x.json())
    # print(x)
    # except Exception:
    # print("Exception in crawl_following!")


def save_db(node):
    """
    store data into mysql
    ---
    args: 
    - node: json object
    """
    # TODO: store into db
    print(node)


def save_csv(node, path):
    """
    store data into csv
    ---
    args: 
    - node: json object
    - path: csv file path
    """
    # TODO: store into csv
    print(node)


def print_format(str, way, width, fill=' ', ed=''):
    try:
        count = 0
        for word in str:
            if (word >= '\u4e00' and word <= '\u9fa5') or word in ['，', '。', '、', '？', '；', '：', '【', '】', '（', '）', '……', '——', '《', '》']:
                count += 1
        width -= count if width >= count else 0
        print('{0,:{1}{2}{3}}'.format(
            str, fill, way, width), end=ed, flush=True)
    except:
        print("Error occurs in print_format()")
