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
    'cookie': open(os.path.join(dir_path, 'cookies.txt')).read()
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
        print("Please copy latest cookie from DevTools of browser to ./cookies.txt!")
        sys.exit(1)

    accessToken = x.json()["data"]["refreshToken"]["accessToken"]
    refreshToken = x.json()["data"]["refreshToken"]["refreshToken"]
    cookies['cookie'] = '_ga=GA1.2.1010923813.1673409584; _gid=GA1.2.564544936.1673409584; fetchRankedUpdate=1673538878642; x-jike-access-token=' + \
        accessToken + '; x-jike-refresh-token=' + refreshToken

    # Write cookie in file
    with open(os.path.join(dir_path, 'cookies.txt'), 'w', encoding="utf8") as f:
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


def sort_nodes(path):
    """
    Sort nodes in time order, from later to earlier
    ---
    args:
    - path: path to json file
    """
    try:
        nodes = read_file(path)

        nodes.sort(key=lambda x: x['createdAt'],  reverse=True)

        with open(path, "w", encoding="utf8") as f:
            for node in nodes:
                save_json(node, path, "a")

        print("Sorted.")
    except Exception:
        print("Not sorted.")


def read_file(path, lines=None):
    """
    read multi-object json file
    ---
    args:
    - path: path to json file
    - lines: lines to read

    return: json object list
    """
    try:
        with open(path, 'r', encoding="utf8") as f:
            count = 0
            x = []
            line = f.readline()

            while(line):
                x.append(json.loads(line))
                count += 1
                line = f.readline()
                if lines and count == lines:
                    break

            print("Read", count, "line(s) from", path)
            return x
    except Exception:
        print("Failed reading file.")


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


# haven't finished yet, but works well
def crawl_posts_fn(user_id, proc_node_fn, op_payload=None, record_count_limit=None, start_time=BASE_TIME, end_time=CURR_TIME, update=False):
    """
    loop and crawl posts from user_id and do something TODO: rewrite
    ---
    args:
    - user_id: Jike user id
    - proc_node_fn: function to process the crawled post
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

    end = False
    add_data = False
    is_first_node = True
    first_node_inserted = False
    request_count = 0
    record_count = 0
    first_node = {}
    
    while True: # pseudo-do-while in python

        x = crawl(url, cookies, headers, payload)
        request_count += 1

        loadMoreKey = x.json()[
            "data"]["userProfile"]["feeds"]["pageInfo"]["loadMoreKey"]
        payload["variables"]["loadMoreKey"] = loadMoreKey
        print(request_count, loadMoreKey)

        for node in x.json()["data"]["userProfile"]["feeds"]["nodes"]:
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
        print(node["content"], time)
        record_count += 1

    if (record_count_limit != None and record_count >= record_count_limit) or (time < start_time):
        end = True

    return end, record_count


def op_post(payload):
    # TODO: optimize code structure

    assert payload is not None

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


# Not used yet...
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
