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
    print("Token expired, trying to refresh cookies...")

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

    accessToken = x.json()["data"]["refreshToken"]["accessToken"]
    refreshToken = x.json()["data"]["refreshToken"]["refreshToken"]
    cookies['cookie'] = '_ga=GA1.2.1010923813.1673409584; _gid=GA1.2.564544936.1673409584; fetchRankedUpdate=1673538878642; x-jike-access-token=' + \
        accessToken + '; x-jike-refresh-token=' + refreshToken

    # Write cookie in file
    with open(os.path.join(dir_path, 'cookies.txt'), 'w', encoding="utf8") as f:
        f.write(cookies['cookie'])
        print("Token updated.")


def handle_errors(x):
    print(x.json()["errors"][0]["extensions"]["code"])

    if x.json()["errors"][0]["extensions"]["code"] == "UNAUTHENTICATED":
        refresh_cookies()
    else:
        print("Unexpected error: ", x.json()["errors"][0]["extensions"])
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


def save_db(x):
    """
    store data into mysql
    ---
    args: 
    - x: json object
    """
    # TODO: store into db
    print(x)


def save_csv(x, path):
    """
    store data into csv
    ---
    args: 
    - x: json object
    - path: csv file path
    """
    # TODO: store into csv
    print(x)


def save_json(x, path, mode, indent=None):
    """
    save json object into json file
    ---
    args: 
    - x: json object
    - path: json file path
    - mode: "a" for add, "w" for overwrite
    - indent: int, default: None
    """
    with open(path, mode, encoding="utf8") as f:
        json.dump(x, f, ensure_ascii=False, indent=indent)
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
