import os
import sys
import json
import requests

from utils import refreshCookies, headers, cookies


dir_path = os.path.dirname(os.path.dirname(__file__))

url = "https://web-api.okjike.com/api/graphql"

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
    try:
        x = requests.post(url, cookies=cookies,
                          headers=headers,
                          data=json.dumps(payload))
        print(x, x.json())
    except requests.exceptions.ConnectionError as e:
        print("Connection error", e.args)
    if ('errors' in x.json()):
        refreshCookies(x)
    return x


def clear_all(post_path):
    # DONE: clear all posts
    # Priority: low, because you can easily delete your account directly
    with open(post_path, 'r', encoding="utf8") as f:
        count = 0
        line = f.readline()
        while (line):
            id = json.loads(line)['id']
            print(id)
            ################# DANGER ZONE ##################
            ################################################
            # uncomment next line to remove all your posts #
            # remove(id) # remove posts by id              #
            ################################################
            count += 1
            line = f.readline()
        print(count, "line(s) operated.")


if __name__ == "__main__":
    post_path = os.path.join(dir_path, "data/posts.json")
    clear_all(post_path)
    # id = "63c0e2ac1c2ecf69b255b6a5"
    # remove(id)
