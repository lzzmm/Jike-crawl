# -*- coding:utf8 -*-
# create at: 2023-02-12T00:56:18Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
from datetime import datetime, timedelta, tzinfo


DIR_PATH = os.path.dirname(os.path.dirname(__file__))

API_GRAPHQL = "https://web-api.okjike.com/api/graphql"
API_USER_PROFILE = "https://api.ruguoapp.com/1.0/users/profile"
API_GET_FOLLOWER_LIST = "https://api.ruguoapp.com/1.0/userRelation/getFollowerList"
API_GET_FOLLOWING_LIST = "https://api.ruguoapp.com/1.0/userRelation/getFollowingList"

HEADERS = {
    'content-type': 'application/json',
    'origin': 'https://web.okjike.com',
    'sec-ch-ua-platform': '"Windows"',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

# updated in utils.py -> def refresh_cookies()
COOKIES = {
    'cookie': open(os.path.join(DIR_PATH, 'config/cookies.txt')).read()
}


############################
#   GraphQL API Payloads   #
############################

PAYLOAD_USER_FEEDS = {
    "operationName": "UserFeeds",
    "query": open(os.path.join(DIR_PATH, "query/query_user_feeds.graphql")).read(),
    "variables": {
        "username": ""
    }
}

PAYLOAD_FETCH_SELF_FEEDS = {
    "operationName": "FetchSelfFeeds",
    "query": open(os.path.join(DIR_PATH, "query/query_fetch_self_feeds.graphql")).read(),
    "variables": {}
}

PAYLOAD_USER_COLLECTIONS = {
    "operationName": "UserCollections",
    "variables": {},
    "query": open(os.path.join(DIR_PATH, "query/query_user_collections.graphql")).read()
}

PAYLOAD_MESSAGE_COMMENTS = {
    "operationName": "MessageComments",
    "variables": {
        "messageId": "",
        "messageType": ""
    },
    "query": open(os.path.join(DIR_PATH, "query/query_message_comments.graphql")).read()
}

PAYLOAD_SUB_COMMENTS = {
    "operationName": "ListSubComments",
    "variables": {
        "targetType": "",
        "commentId": ""
    },
    "query": open(os.path.join(DIR_PATH, "query/query_list_sub_comments.graphql")).read()
}

PAYLOAD_REFRESH_COOKIES = {
    "operationName": "refreshToken",
    "variables": {},
    "query": "mutation refreshToken {\n  refreshToken {\n    accessToken\n    refreshToken\n  }\n}\n"
}

PAYLOAD_LIST_NOTIFICATION = {
    "operationName": "ListNotification",
    "variables": {},
    "query": open(os.path.join(DIR_PATH, "query/query_notifications.graphql")).read()
}

PAYLOAD_LIKE = {
    "operationName": "LikeMessage",
    "query": "mutation LikeMessage($messageType: MessageType!, $id: ID!) {        likeMessage(messageType: $messageType, id: $id)    }        ",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    }
}

PAYLOAD_UNLIKE = {
    "operationName": "UnlikeMessage",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    },
    "query": "mutation UnlikeMessage($messageType: MessageType!, $id: ID!) {\n  unlikeMessage(messageType: $messageType, id: $id)\n}\n"
}

PAYLOAD_RELATED_KEYWORDS = {
    "operationName": "SearchReleatedKeywords",
    "variables": {
        "keywords": ""
    },
    "query": "query SearchReleatedKeywords($keywords: String!) {\n  search {\n    relatedKeywordTips(keywords: $keywords) {\n      type\n      description\n      icon\n      suggestion\n      url\n      __typename\n    }\n    __typename\n  }\n}\n"
}

PAYLOAD_SEARCH_INTEGRATE = {
    "operationName": "SearchIntegrate",
    "variables": {
        "keywords": ""
    },
    "query": open(os.path.join(DIR_PATH, "query/query_search_integrate.graphql")).read()
}

PAYLOAD_MEDIA_META_PLAY = {
    "operationName": "MediaMetaPlay",
    "variables": {
        "messageId": "",
        "messageType": "ORIGINAL_POST"
    },
    "query": "query MediaMetaPlay($messageId: ID!, $messageType: MessageType!) {\n  mediaMetaPlay(messageId: $messageId, messageType: $messageType) {\n    mediaLink\n    url\n    __typename\n  }\n}\n"
}

PAYLOAD_HIDE = {
    # TODO: Does not work
    "operationName": "HideMessage",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": "63e4ee1a74aa215f9158864e"
    },
    "query": "mutation HideMessage($id: ID!, $messageType: MessageType!) {\n  hideMessage(messageType: $messageType, id: $id)\n}\n"
}


############################
#   datetime & timezone    #
############################

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class UTC(tzinfo):
    def utcoffset(self, dt) -> timedelta:
        return ZERO

    def tzname(self, dt) -> str:
        return 'UTC'

    def dst(self, dt) -> timedelta:
        return ZERO

    def fromutc(self, dt) -> timedelta:
        return dt


class GMT8(tzinfo):
    def utcoffset(self, dt) -> timedelta:
        return HOUR * 8

    def tzname(self, dt) -> str:
        return 'GMT+8'

    def dst(self, dt) -> timedelta:
        return ZERO

    def fromutc(self, dt) -> timedelta:
        return dt + dt.utcoffset()


BASE_TIME = datetime(2015, 3, 28, tzinfo=GMT8())  # Jike 1.0 online
BASE_YEAR = BASE_TIME.year
CURR_TIME = datetime.now(GMT8())  # current time
CURR_YEAR = CURR_TIME.year
