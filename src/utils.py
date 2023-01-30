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


def read_file(path, lines=None):
    """
    read multi-object json file
    ---
    args:
    - path: path to json file
    - lines: lines to read
    
    return: json object list
    """
    with open(path, 'r', encoding="utf8") as f:
        count = 0
        x = []
        line = f.readline()

        while (line):
            x.append(json.loads(line))
            count += 1
            line = f.readline()
            if lines and count == lines:
                break

        print("Read", count, "line(s) from", path)
        return x


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
        count += 1
        # with open (os.path.join(pic_path, str(count)), 'wb') as f:
        with open (os.path.join(pic_path, picUrl.split("?")[0].split("/")[-1]), 'wb') as f:
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
