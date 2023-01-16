import os
import sys
import json
import requests


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


def refreshCookies(x):
    print(x.json()["errors"][0]["extensions"]["code"])
    if x.json()["errors"][0]["extensions"]["code"] == "UNAUTHENTICATED":
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
        with open(os.path.join(dir_path, 'cookies.txt'), 'w', encoding="utf8") as f:
            f.write(cookies['cookie'])
        print("Token updated.")
    else:
        print("Unexpected error: ", x.json()["errors"][0]["extensions"])
        sys.exit(1)
