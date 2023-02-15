# Jike-crawl

> **Note** TEMPORARILY NO TIME TO MAINTAIN

![post_html](img/post_html.png)


TODO:

1. rewrite some funtctions
2. update zh-cn README

## RUNNING VIA `src/main.ipynb` IS STRONGLY RECOMMENDED

## Jike-crawl (EN)

[中文](#删号跑路中文)

Crawl posts, notifications, and maybe collections on Jike and save them into `csv file`(undone) / `json file` / `MySQL`(undone) before you delete your Jike account. Pictures in posts can be downloaded, too.

Show data in a HTML page and export as PDF.

![post_html](img/posts_save_pdf.png)

Delete posts in a specific time range or by default, all time.

Count and analysis(undone) infomations and posts.

Maybe using NLP for sentiment analysis(undone).

![post_data](img/posts_data.png)

Timezone is set to GMT+8.

### Requirements

- Python 3
- json
- requests

Download and setup Python environment. Open this folder in Visual Studio Code.

Install packages from [PyPI](https://pypi.org/).

Or you can run

```shell
pip install -r requirements.txt
```

### Run

Login to [Jike Website](https://web.okjike.com/), press `F12` to open DevTools. Switch to `Network` tab, filter `Fetch/XHR`, refresh the page, then there will be some requests on it.

Select one `profile?username=...` request and copy `username` from `Request URL` into `id` in `main()` in `src/crawl.py` file.

Select one `graphql` request and copy value of `cookie` from `Request headers` into `config/cookies.txt` file.

![devtools](img/devtools.png)

#### Crawl

Choose operations and set `user_id` in `main()` of `src/crawl.py`.

If you want to **save pictures** in posts you can set `b_save_pics` in `main()` of `src/crawl.py` `True` (default is `False`).

If enabled `b_save_pics`, pictures in posts will be stored into `data/pics`.

You can crawl data in specific time range by modifiding `start_time` and `end_time`.

`BASE_TIME` is the time when Jike launched so normally no data was generated before that time.

`CURR_TIME` is the time when the program is executing this line, or say, now.

```python
class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
```

You can construct a datetime object like

```python
# class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
datetime(2021, 1, 1, tzinfo=GMT8()) #  2021/01/01 00:00:00.000 (+08:00)
datetime(2021, 1, 1, 12, 13, 14, 15, tzinfo=GMT8()) # 2021/01/01 12:13:14.000015 (+08:00)
```

Or use `CURR_TIME` or `BASE_TIME` with a time delta like

```python
# class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
time_delta = timedelta(days=30)
end_time = CURR_TIME - time_delta
```

to operate posts created before 30 days ago.

For example, if you'd like to crawl 10 latest posts posted during 2022/01/01-2022/06/26, you can write this

```python
    post_start_time = datetime(2022, 1, 1, tzinfo=GMT8())
    post_end_time = datetime(2022, 6, 26, tzinfo=GMT8())
    post_record_limit = 10
    crawl_posts(user_id, post_path, "a", post_record_limit, post_start_time, post_end_time)
```

If you're in `/src`, then run:

```shell
python -u ./crawl.py
```

#### Analysis

Run `src/data_analysis.py`.

You can also modified code in that file to get statistics you want.

#### Delete posts

Only after you crawled posts data, you can delete these posts by their id.

Open `delete_posts.py`, set `post_path` in `main()` a path to the json file which stores posts data.

You can delete data in specific time range by modifiding `start_time` and `end_time`.

For more details please see [Crawl](https://github.com/lzzmm/Jike-crawl#crawl) on above.

Follow instruction in `clear()` uncomment this line in DANGER ZONE

```python
# remove(id) # remove posts by id
```

run `delete_posts.py`。

#### Like / unlike posts from user list

Edit user name in `config/user_name_list.txt`

run `like_posts.py`

## 删号跑路（中文）

[EN](#jike-crawl-en)

### 建议通过 `src/main.ipynb` 运行

在注销即刻账号跑路之前保存自己的动态和消息。

统计并生成报告。

批量删除动态。

![posts_data](img/posts_data.png)

### 环境

- Python 3
- json
- requests

注：`requests` 安装的两种方式，以下均在命令提示符(cmd)中进行。

1. 直接安装

    ```shell
    pip install -r requirements.txt
    ```

2. 下载安装

    下载 `requests` 安装包，进入安装包所在路径，运行以下命令

    ```shell
    pip install
    ```

### 初次运行，保存数据

1. 进入开发者模式。在 [即刻网页版](https://web.okjike.com/) 中登录自己的即刻账号，并进入个人主页。按 `F12` 打开开发者工具。切换到 `网络(Network)`，过滤 `Fetch/XHR`，刷新页面，此时下方会出现请求列表，罗列了请求的名称、状态等信息。

2. 获取cookie。在请求列表中，任选一个名称为 `graphql` 的请求，单击 `标头(Headers)`，找到 `cookie` 字段并复制全文，粘贴到 `Jike-crawl/config/cookies.txt`。

    ![devtools](img/devtools_cn.png)

3. 获取id。在请求列表中，任选一个名称为 `profile?username=...` 的请求，单击 `响应(Response)`，复制 `username` 字段:后的内容，粘贴到 `src/crawl.py`中 `main()` 函数里的 `user_id`。

4. 保存数据到本地。

    如果您想要保存动态中的图片，在 `src/crawl.py` 的 `main()` 里设置 `b_save_pics` 为 `True` （默认是`False`）。

    您可以通过修改 `start_time` 和 `end_time` 来保存特定时间段内发布的动态。

    `BASE_TIME` 是即刻 1.0 上线的时间，理论上没有动态会在那之前发布。

    `CURR_TIME` 是现在的时间。

    ```python
    class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
    class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    ```

    您可以像下面所示构建 `datetime` 对象：

    ```python
    # class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
    datetime(2021, 1, 1, tzinfo=GMT8()) #  2021/01/01 00:00:00.000 (+08:00)
    datetime(2021, 1, 1, 12, 13, 14, 15, tzinfo=GMT8()) # 2021/01/01 12:13:14.000015 (+08:00)
    ```

    或者使用 `CURR_TIME` 或/和 `BASE_TIME` 加上/减去 `timedelta`，下面展示了拉取 30 天之前的动态的设置。

    ```python
    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    time_delta = timedelta(days=30)
    end_time = CURR_TIME - time_delta
    ```

    下面展示了爬取 2022/01/01 至 2022/06/26 的 10 个最近的动态。

    ```python
        post_start_time = datetime(2022, 1, 1, tzinfo=GMT8())
        post_end_time = datetime(2022, 6, 26, tzinfo=GMT8())
        post_record_limit = 10
        crawl_posts(user_id, post_path, "a", post_record_limit, post_start_time, post_end_time)
    ```

    运行 `src/crawl.py` 。（打开 `src/crawl.py` ，右键选择在终端中运行；或输入命令 `python -u [python_file_path]`）

    `crawl.py` 文件中的 `main()` 函数将把消息列表和个人动态**追加**到 `data/notifications.json` 和 `data/post.json` 中。

    ```python
    crawl_notifications(noti_path) # 拉取消息列表
    crawl_posts(post_path, user_id) # 拉取个人动态
    ```

    注：如需重新拉取请先清空上述两个文件中的内容。如不需要拉取消息或动态，可注释对应行代码。

#### 数据分析

必须先运行 `crawl.py` 保存数据，方可进行数据分析。

运行 `src/data_analysis.py`。

您可以修改该文件得到自己想要的统计，如获取评论您最多的用户等。

#### 删除动态

必须先运行 `crawl.py` 保存数据，方可进行动态删除。

此操作仅可根据本地保存的数据进行删除。即在新发动态后，如果没有重新拉取，则无法删除。

1. 若想删除所有动态，请跳过此步。若想修改动态删除的时间范围，请打开 `src/delete_posts.py` 将 `main()` 函数中的 `start_time`（开始时间）和 `end_time`（结束时间）修改为所需的日期(也可详细设定时间）。

2. 将 `main()` 函数中 `post_path` 修改为储存在本地的 `posts.json` 的路径。

3. 取消 `clear()` 函数中 DANGER ZONE 中的这行注释（按 `Ctrl` + `/` 或删掉这行前面的 `#` 和一个空格）。

    ```python
    ################# DANGER ZONE ##################
    ################################################
    # uncomment next line to remove all your posts #
    # remove(id) # remove posts by id              #
    ################################################
    ```

4. 运行 `delete_posts.py`。

## Acknowledgement

特别感谢即友 [愚笨的路人粥](https://web.okjike.com/u/fe3cf5ee-1565-44f5-be3f-d65f1236687b) (Github[@Jellower](https://github.com/Jellower)) 协助完成中文文档。

## Appendices

### Blog

[周报 #0x01:删号跑路](https://lzzmm.github.io/2023/01/16/weekly-review-1/#project%E5%88%A0%E5%8F%B7%E8%B7%91%E8%B7%AF)

### datetime

[docs of datetime](https://docs.python.org/zh-cn/3/library/datetime.html)

### ignore cookies.txt

```sh
git update-index --assume-unchanged config/cookies.txt
```

### query

`web.okjike.com` uses [GraphQL](https://graphql.cn/learn/queries/) for query.

In folder `query`, there're two types of text files. One with suffix `_original` means that query is used by `web.okjike.com` originally and with too much useless content and avatar urls. Others are used in this project to get useful content.

#### query infomations

payload

```json
{
    "operationName": "ListNotification",
    "query": "query/query_notifications_original.txt",
    "variables": {}
}
```

returns

`"loadMoreKey"` returns `"lastNotificationId"` which can be used to load more.

`"nodes"` contains an array of notifications.

`"id"` maybe the unique key of notifications.

`"referenceItem"` what this notification references to, maybe your post or your comment. If it references to a comment, then `"targetId"` will be the original post id (or see `"targetType"` which will be `"ORIGINAL_POST"`).

`"type"`:

- `"LIKE_PERSONAL_UPDATE"` a user liked your post.
- `"COMMENT_PERSONAL_UPDATE"` a user commented on your post.
- `"LIKE_PERSONAL_UPDATE_COMMENT"` a user liked your comment.
- `"REPLIED_TO_PERSONAL_UPDATE_COMMENT"` a user replied to your comment. Picture will not be shown.
- `"AVATAR_GREET"`
- `"USER_FOLLOWED"` a user followed you
- `"USER_SILENT_FOLLOWED"` a user without `linkUrl` followed you
- `"CURIOSITY_REPLIED_MY_MENTIONING"` on web page, unlike app, it will not show any content.
- `"CURIOSITY_ANSWER_REACTION"` reacted to my answer.
- `"CURIOSITY_MENTION_ME_ANSWER"` asked me to answer.

If `"actionType": "USER_LIST"` then `"actionItem"` will be a list of users liked this post or comment.

If `"actionType": "COMMENT"` then `"actionItem"` will be a comment, also with a user in `users` list.

example (a node)

```json
{
    "id": "63c12cd91a751832db20b0f4",
    "type": "LIKE_PERSONAL_UPDATE",
    "createdAt": "2023-01-13T10:05:13.290Z",
    "updatedAt": "2023-01-13T10:05:13.290Z",
    "linkType": "ORIGINAL_POST",
    "referenceItem": {
        "content": "谢谢owo\n也祝即刻2023兔飞猛进",
        "id": "63c0f52f02bc713efb705fa6",
        "targetId": null,
        "targetType": null,
        "type": "ORIGINAL_POST",
        "__typename": "NotificationReferenceItem"
    },
    "actionType": "USER_LIST",
    "actionItem": {
        "type": "LIKE",
        "usersCount": 9,
        "users": [
        {
            "screenName": "闪光橙橙.",
            "username": "03B35874-5BE2-4E2E-8417-2E4AD8BB38FF",
            "__typename": "User"
        },
        {
            "screenName": "是周同学",
            "username": "EC62A3C7-4C25-45E4-B41F-15C5D3338C4F",
            "__typename": "User"
        },
        {
            "screenName": "夜神游",
            "username": "587e69bd-547a-4917-8327-7175686e5c36",
            "__typename": "User"
        }
        ],
        "__typename": "NotificationDefaultActionItem"
    },
    "__typename": "Notification"
}
```

#### query user feeds

payload

```json
{
    "operationName": "UserFeeds",
    "query": "query/query_user_feeds_original.txt",
    "variables": {
        "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC",
        "loadMoreKey": {
            "lastId": "63a450102559c538e1bd3482"
        }
    }
}
```

returns example (a node)

```json
{
  "id": "63c0f52f02bc713efb705fa6",
  "type": "ORIGINAL_POST",
  "content": "谢谢owo\n也祝即刻2023兔飞猛进",
  "shareCount": 0,
  "repostCount": 0,
  "createdAt": "2023-01-13T06:07:43.956Z",
  "pictures": [
    {
      "picUrl": "https://cdnv2.ruguoapp.com/FifvSKjQ4BRk3mF5ZzoWNstF6FX-v3.jpg"
    }
  ],
  "urlsInText": [],
  "liked": true,
  "likeCount": 10,
  "commentCount": 5,
  "topic": {
    "id": "5665185bbab9191200b71460",
    "content": "帮扶即刻做大做强计划"
  }
}
```

#### query message detail

payload

```json
{
    "operationName": "MessageDetail"
    "query": "query/query_message_detail_original.txt",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "messageId": "63a3b8b160f43c294d672622"
    }
}
```

#### query message comments

payload

```json
{
    "operationName": "MessageComments",
    "query": "query/query_message_comments_original.txt",
    "variables": {
        "messageId": "6389d93582742179e6a9335c",
        "messageType": "ORIGINAL_POST"
    }
}
```

#### remove message

payload

```json
{
    "operationName": "RemoveMessage",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": "63872d0c02237e4e5813435d"
    },
    "query": "mutation RemoveMessage($id: ID!, $messageType: MessageType!) {\n  removeMessage(messageType: $messageType, id: $id) {\n    toast\n    __typename\n  }\n}\n"
}
```

#### like

payload

```json
{
    "operationName": "LikeMessage",
    "query": "mutation LikeMessage($messageType: MessageType!, $id: ID!) {        likeMessage(messageType: $messageType, id: $id)    }        ",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    }
}
```

#### unlike

payload

```json
{
    "operationName": "UnlikeMessage",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    },
    "query": "mutation UnlikeMessage($messageType: MessageType!, $id: ID!) {\n  unlikeMessage(messageType: $messageType, id: $id)\n}\n"
}
```

#### collect & uncollect

payload

```json
{
    "operationName": "CollectMessage",
    "variables": {
        "messageId": "63e4ee1a74aa215f9158864e",
        "messageType": "ORIGINAL_POST"
    },
    "query": "mutation CollectMessage($messageType: MessageType!, $messageId: ID!) {\n  collectMessage(messageType: $messageType, id: $messageId)\n}\n"
}
```

```json
{
    "operationName": "UncollectMessage",
    "variables": {
        "messageId": "63e4ee1a74aa215f9158864e",
        "messageType": "ORIGINAL_POST"
    },
    "query": "mutation UncollectMessage($messageType: MessageType!, $messageId: ID!) {\n  uncollectMessage(messageType: $messageType, id: $messageId)\n}\n"
}
```

#### Self Complete Profile

```json
{
    "operationName": "SelfCompleteProfile",
    "variables": {},
    "query": "query SelfCompleteProfile {\n  profile {\n    ...CompleteuserFragment\n    __typename\n  }\n}\n\nfragment CompleteuserFragment on UserInfo {\n  username\n  screenName\n  briefIntro\n  city\n  country\n  gender\n  following\n  isSponsor\n  verifyMessage\n  backgroundImage {\n    picUrl\n    __typename\n  }\n  statsCount {\n    followedCount\n    followingCount\n    topicSubscribed\n    respectedCount\n    __typename\n  }\n  profileTags {\n    picUrl\n    text\n    type\n    __typename\n  }\n  avatarImage {\n    thumbnailUrl\n    picUrl\n    __typename\n  }\n  __typename\n}\n"
}
```

#### Miss feeds

payload

```json
{
    "operationName": "MissedFeeds",
    "variables": {},
    "query": "query/query_miss_feeds_original.txt"
}
```

result

```json
{
    "data": {
        "viewer": {
            "followingUpdates": {
                "pageInfo": {
                    "loadMoreKey": {
                        "session": "PopulatedUpdate",
                        "lastPageEarliestTime": 1675782359000,
                        "lastReadTime": 1675827415908
                    },
                    "hasNextPage": true,
                    "__typename": "PageInfo"
                },
                "nodes": [
                    {
                        "id": "",
                        "type": "ORIGINAL_POST",
                        "content": "",
                        "shareCount": 0,
                        "repostCount": 0,
                        "createdAt": "2023-02-08T03:30:59.716Z",
                        "collected": false,
                        "pictures": [
                            {
                                "format": "jpeg",
                                ...
                                "picUrl": "",
                                "width": 1080,
                                "height": 1223,
                                "__typename": "PictureInfo"
                            }
                        ],
                        "urlsInText": [],
                        "__typename": "OriginalPost",
                        "liked": false,
                        "likeCount": 1,
                        "commentCount": 0,
                        "topic": {
                            "id": "",
                            "content": "AIGC探索站",
                            "__typename": "TopicInfo"
                        },
                        "readTrackInfo": {
                            "storyStatus": "NONE",
                            "loadedAt": 1675827441634,
                            "feedType": "FOLLOWING_UPDATES"
                        },
                        "user": {
                            "avatarImage": {
                                ...
                            },
                            "isSponsor": true,
                            "username": "",
                            "screenName": "",
                            "briefIntro": "",
                            "__typename": "User"
                        },
                        "video": null,
                        "linkInfo": null,
                        "isPrivate": null,
                        "pinned": null
                    },
                    ...
                ]
            }
        }
    }
}

```

#### Fetch self feeds

payload

```json
{
    "operationName": "FetchSelfFeeds",
    "variables": {},
    "query": "query/query_fetch_self_feeds_original.txt"
}
```

#### User collections

payload

```json
{
    "operationName": "UserCollections",
    "variables": {},
    "query": "query/query_user_collections_original.txt"
}
```

result

```json
{
    "data": {
        "viewer": {
            "collections": {
                "pageInfo": {
                    "loadMoreKey": {
                        "_id": "639e2175d6de7b3c57347a9e",
                        "createdAt": "2022-12-17T20:07:17.409Z"
                    },
                    "hasNextPage": true,
                    "__typename": "PageInfo"
                },
                "nodes": [
                    {
                        "id": "62ea9e354d572a90dd9f147c",
                        "type": "ORIGINAL_POST",
                        "content": "或许可以出一个功能，就是把账号内容归档然后不让别人看。",
                        "shareCount": 0,
                        "repostCount": 1,
                        "createdAt": "2022-08-03T16:11:33.861Z",
                        "collected": true,
                        "pictures": [],
                        "urlsInText": [],
                        "__typename": "OriginalPost",
                        "liked": true,
                        "likeCount": 4,
                        "commentCount": 8,
                        "topic": {
                            "id": "5a2114605a41da0016de2f4c",
                            "content": "我来做即刻产品经理",
                            "__typename": "TopicInfo"
                        },
                        "readTrackInfo": null,
                        "user": {
                            "avatarImage": {
                                "thumbnailUrl": "https://cdnv2.ruguoapp.com/Fov1JGbHDr5vNXbQ7bZD1B9kGpWSv2.png?imageMogr2/auto-orient/heic-exif/1/format/jpeg/thumbnail/!120x120r/gravity/Center/crop/!120x120a0a0",
                                "smallPicUrl": "https://cdnv2.ruguoapp.com/Fov1JGbHDr5vNXbQ7bZD1B9kGpWSv2.png?imageMogr2/auto-orient/heic-exif/1/format/jpeg/thumbnail/!300x300r/gravity/Center/crop/!300x300a0a0",
                                "picUrl": "https://cdnv2.ruguoapp.com/Fov1JGbHDr5vNXbQ7bZD1B9kGpWSv2.png?imageMogr2/auto-orient/heic-exif/1/format/jpeg/thumbnail/!1000x1000r/gravity/Center/crop/!1000x1000a0a0",
                                "__typename": "AvatarImage"
                            },
                            "isSponsor": true,
                            "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC",
                            "screenName": "慵懒致命之炸毛",
                            "briefIntro": "CS(HPC)@SYSU\n小镇摸鱼家的日常\n弱小，但是还年轻",
                            "__typename": "User"
                        },
                        "video": null,
                        "linkInfo": null,
                        "isPrivate": null,
                        "pinned": null
                    },
                    ...
                ]
            }
        }
    }
}
```

#### Latest respect

payload

```json
{
    "operationName": "LatestRespect",
    "variables": {
        "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
    },
    "query": "query LatestRespect($username: String!, $loadMoreKey: JSON) {\n  userProfile(username: $username) {\n    username\n    latestRespected(loadMoreKey: $loadMoreKey) {\n      pageInfo {\n        loadMoreKey\n        __typename\n      }\n      nodes {\n        id\n        content\n        createdAt\n        user {\n          id\n          ...TinyUserFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TinyUserFragment on UserInfo {\n  avatarImage {\n    thumbnailUrl\n    smallPicUrl\n    picUrl\n    __typename\n  }\n  isSponsor\n  username\n  screenName\n  briefIntro\n  __typename\n}\n"
}
```

result

```json
{
    "data": {
        "userProfile": {
            "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC",
            "latestRespected": {
                "pageInfo": {
                    "loadMoreKey": null,
                    "__typename": "PageInfo"
                },
                "nodes": [
                    {
                        "id": "625e85371346e432d8fb2091",
                        "content": "要一直坚持自己的喜爱呀_(:D」∠)_",
                        "createdAt": "2022-04-19T09:47:35.517Z",
                        "user": {
                            "id": "5ee065b245f1b200176e199a",
                            "avatarImage": {
                                "thumbnailUrl": "https://cdnv2.ruguoapp.com/FgQw2a68x5atpplts9DdtKekmjzI.jpeg?imageMogr2/auto-orient/heic-exif/1/format/jpeg/thumbnail/!120x120r/gravity/Center/crop/!120x120a0a0",
                                "smallPicUrl": "https://cdnv2.ruguoapp.com/FgQw2a68x5atpplts9DdtKekmjzI.jpeg?imageMogr2/auto-orient/heic-exif/1/format/jpeg/thumbnail/!300x300r/gravity/Center/crop/!300x300a0a0",
                                "picUrl": "https://cdnv2.ruguoapp.com/FgQw2a68x5atpplts9DdtKekmjzI.jpeg?imageMogr2/auto-orient/heic-exif/1/format/jpeg/thumbnail/!1000x1000r/gravity/Center/crop/!1000x1000a0a0",
                                "__typename": "AvatarImage"
                            },
                            "isSponsor": true,
                            "username": "4bfdb180-691c-47f0-bd00-817926a9e539",
                            "screenName": "永远喜欢温迪",
                            "briefIntro": "我想一个人静静地消失",
                            "__typename": "User"
                        },
                        "__typename": "Respect"
                    },
                    ...
                ],
                "__typename": "RespectConnection"
            },
            "__typename": "User"
        }
    }
}
```

#### List respect

```json
{
    "operationName": "ListRespect",
    "variables": {
        "username": "D5560B5D-7448-4E1A-B43A-EC2D2C9AB7EC"
    },
    "query": "query ListRespect($username: String!, $loadMoreKey: JSON) {\n  userProfile(username: $username) {\n    username\n    respects(loadMoreKey: $loadMoreKey) {\n      pageInfo {\n        loadMoreKey\n        __typename\n      }\n      nodes {\n        id\n        content\n        createdAt\n        user {\n          ...TinyUserFragment\n          __typename\n        }\n        targetUser {\n          id\n          ...TinyUserFragment\n          bio\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TinyUserFragment on UserInfo {\n  avatarImage {\n    thumbnailUrl\n    smallPicUrl\n    picUrl\n    __typename\n  }\n  isSponsor\n  username\n  screenName\n  briefIntro\n  __typename\n}\n"
}
```

#### search related keywords (users / topics)

payload

```json
{
    "operationName": "SearchReleatedKeywords",
    "variables": {
        "keywords": "是周同学"
    },
    "query": "query SearchReleatedKeywords($keywords: String!) {\n  search {\n    relatedKeywordTips(keywords: $keywords) {\n      type\n      description\n      icon\n      suggestion\n      url\n      __typename\n    }\n    __typename\n  }\n}\n"
}
```

returns 1/3

```json
{
    "data": {
        "search": {
            "relatedKeywordTips": [
                {
                    "type": "user",
                    "description": null,
                    "icon": "https://cdnv2.ruguoapp.com/Fl1Y3GCIC5YJuH3z3L9_2u3pzUyg.png",
                    "suggestion": "用户：是周同学",
                    "url": "/u/EC62A3C7-4C25-45E4-B41F-15C5D3338C4F",
                    "__typename": "SearchRelatedKeyword"
                },
                {
                    "type": "keyword",
                    "description": null,
                    "icon": "https://cdnv2.ruguoapp.com/Fn1nrT-XM1l46Y4sFfFnEBJBZXg5.png",
                    "suggestion": "是周同学",
                    "url": "/search?type=integrated&keywords=%E6%98%AF%E5%91%A8%E5%90%8C%E5%AD%A6",
                    "__typename": "SearchRelatedKeyword"
                }
            ],
            "__typename": "Search"
        }
    }
}
```

returns 2/3

```json
{
    "data": {
        "search": {
            "relatedKeywordTips": [
                {
                    "type": "keyword",
                    "description": null,
                    "icon": "https://cdnv2.ruguoapp.com/Fn1nrT-XM1l46Y4sFfFnEBJBZXg5.png",
                    "suggestion": "炸毛",
                    "url": "/search?type=integrated&keywords=%E7%82%B8%E6%AF%9B",
                    "__typename": "SearchRelatedKeyword"
                }
            ],
            "__typename": "Search"
        }
    }
}
```

returns 3/3

```json
{
    "data": {
        "search": {
            "relatedKeywordTips": [
                {
                    "type": "topic",
                    "description": "100万+人加入",
                    "icon": "https://cdnv2.ruguoapp.com/FtiOcV3mCD0eNy8yu7nK0YUfYLyR.png",
                    "suggestion": "圈子：读书会",
                    "url": "/topic/5a158e62a0ef4f00117ab145?ref=SEARCH_KEYWORDTIP",
                    "__typename": "SearchRelatedKeyword"
                },
                {
                    "type": "keyword",
                    "description": null,
                    "icon": "https://cdnv2.ruguoapp.com/Fn1nrT-XM1l46Y4sFfFnEBJBZXg5.png",
                    "suggestion": "读书会",
                    "url": "/search?type=integrated&keywords=%E8%AF%BB%E4%B9%A6%E4%BC%9A",
                    "__typename": "SearchRelatedKeyword"
                }
            ],
            "__typename": "Search"
        }
    }
}
```

error

```json
{
    "errors": [
        {
            "message": "Expected a value of type \"SearchRelatedKeywordType\" but received: \"recruitment\"",
            "locations": [
                {
                    "line": 4,
                    "column": 7
                }
            ],
            "path": [
                "search",
                "relatedKeywordTips",
                0,
                "type"
            ],
            "extensions": {
                "code": "INTERNAL_SERVER_ERROR"
            }
        }
    ],
    "data": {
        "search": {
            "relatedKeywordTips": null,
            "__typename": "Search"
        }
    }
}
```

#### Search Integrate

```json
{
    "operationName": "SearchIntegrate",
    "variables": {
        "keywords": "炸毛"
    },
    "query": "query/query_search_integrate_original.txt"
}
```
