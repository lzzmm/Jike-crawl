import os
import sys
import json
import requests

from utils import refreshCookies, headers, cookies
from delete_posts import clear_all


dir_path = os.path.dirname(os.path.dirname(__file__))


url = "https://web-api.okjike.com/api/graphql"


json_indent = 2


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
    return x


def save_db(x):
    """
    store data into mysql
    ---
    args: 
    - x: response object
    """
    # TODO: store into db
    print(x)


def save_csv(x, path):
    """
    store data into csv
    ---
    args: 
    - x: response object
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



def crawl_notifications(path):
    """
    loop and crawl all notifications and save into database/file
    ---
    args:
    - path: file path 
    """

    payload = {
        "operationName": "ListNotification",
        "variables": {},
        "query": open(os.path.join(dir_path, "query/query_notifications.txt")).read()
    }

    count = 1
    x = crawl(url, cookies, headers, payload)
    if 'errors' in x.json():  # The "has_key" method has been removed in Python 3
        refreshCookies(x)
        x = crawl(url, cookies, headers, payload)
    loadMoreKey = x.json()[
        "data"]["viewer"]["notifications"]["pageInfo"]["loadMoreKey"]
    for node in x.json()["data"]["viewer"]["notifications"]["nodes"]:
        save_json(node, path, "a")
        print("Witten in \"" + path + "\".")

    while loadMoreKey != None:  # 'hasNextPage': True
        payload["variables"]["loadMoreKey"] = loadMoreKey
        print(count, loadMoreKey)
        x = crawl(url, cookies, headers, payload)
        if 'errors' in x.json():
            refreshCookies(x)
            x = crawl(url, cookies, headers, payload)
        loadMoreKey = x.json()[
            "data"]["viewer"]["notifications"]["pageInfo"]["loadMoreKey"]
        if x.json()["data"]["viewer"]["notifications"]["nodes"]:
            for node in x.json()["data"]["viewer"]["notifications"]["nodes"]:
                save_json(node, path, "a")
        print("Witten in \"" + path + "\".")
        count += 1
    print(count, "request(s) was(were) sent.")


def crawl_posts(path, user_id=None, remove=False):
    """
    loop and crawl all notifications and save into database/file
    ---
    args:
    - path: file path 
    - user_id: Jike user id
    - remove: if true, remove all posts
    """

    payload = {
        "operationName": "UserFeeds",
        "query": open(os.path.join(dir_path, "query/query_user_feeds.txt")).read(),
        "variables": {
            "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC",
            # "loadMoreKey": {
            #     "lastId": "63a450102559c538e1bd3482"
            # }
        }
    }

    if user_id:
        payload["variables"]["username"] = user_id

    count = 1
    x = crawl(url, cookies, headers, payload)
    if 'errors' in x.json():
        refreshCookies(x)
        x = crawl(url, cookies, headers, payload)
    loadMoreKey = x.json()[
        "data"]["userProfile"]["feeds"]["pageInfo"]["loadMoreKey"]
    for node in x.json()["data"]["userProfile"]["feeds"]["nodes"]:
        save_json(node, path, "a")
        print("Witten in \"" + path + "\".")

    while loadMoreKey != None:  # 'hasNextPage': True
        payload["variables"]["loadMoreKey"] = loadMoreKey
        print(count, loadMoreKey)
        x = crawl(url, cookies, headers, payload)
        if 'errors' in x.json():
            refreshCookies(x)
            x = crawl(url, cookies, headers, payload)
        loadMoreKey = x.json()[
            "data"]["userProfile"]["feeds"]["pageInfo"]["loadMoreKey"]
        if x.json()["data"]["userProfile"]["feeds"]["nodes"]:
            for node in x.json()["data"]["userProfile"]["feeds"]["nodes"]:
                save_json(node, path, "a")
        print("Witten in \"" + path + "\".")
        count += 1
    print(count, "request(s) was(were) sent.")


if __name__ == "__main__":
    noti_path = os.path.join(dir_path, "data/notifications.json")
    post_path = os.path.join(dir_path, "data/posts.json")
    user_id = "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC" # replace with your own Jike user id
    
    crawl_notifications(noti_path)
    crawl_posts(post_path, user_id)
    
    # goto "delete_posts.py" and manually enable remove()
    # clear_all(post_path)
