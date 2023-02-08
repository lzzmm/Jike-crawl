# -*- coding:utf8 -*-
# create at: 2023-02-07T16:02:19Z+08:00
# author:    lzzmm<2313681700@qq.com>


from utils import *


payload_like = {
    "operationName": "LikeMessage",
    "query": "mutation LikeMessage($messageType: MessageType!, $id: ID!) {        likeMessage(messageType: $messageType, id: $id)    }        ",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    }
}

payload_unlike = {
    "operationName": "UnlikeMessage",
    "variables": {
        "messageType": "ORIGINAL_POST",
        "id": ""
    },
    "query": "mutation UnlikeMessage($messageType: MessageType!, $id: ID!) {\n  unlikeMessage(messageType: $messageType, id: $id)\n}\n"
}


def like(user_id, miss_feed_only=False, record_limit=5, start_time=BASE_TIME, end_time=CURR_TIME):

    crawl_posts_fn(user_id,
                   proc_node_fn,
                   payload_like,
                   miss_feed_only=miss_feed_only,
                   record_count_limit=record_limit,
                   start_time=start_time,
                   end_time=end_time)


def unlike(user_id, miss_feed_only=False, record_limit=5, start_time=BASE_TIME, end_time=CURR_TIME):

    crawl_posts_fn(user_id,
                   proc_node_fn,
                   payload_unlike,
                   miss_feed_only=miss_feed_only,
                   record_count_limit=record_limit, start_time=start_time,
                   end_time=end_time)


# DONE: search by name, multi user supports
# TODO: record last post, and reconstruct functions
#       threading
#       miss_feed_only haven't tested yet
#       fishball: 或者把好友列表取出来放文件里
#                 FAILED: 暂时找不到新版 getFollowingList 接口


if __name__ == "__main__":
    start_time = CURR_TIME - timedelta(days=1)  # datetime
    end_time = CURR_TIME    # datetime
    record_limit = 5        # int or None
    # like too many posts from a user in a short time
    # may make that user feel troubled
    miss_feed_only = False

    # crawl_following()  # haven't done yet

    # user_id_list = read_list_file(os.path.join(
    # dir_path, "cfgfiles/user_id_list.txt"))

    # call if you have changed "cfgfiles/user_name_list.txt"
    user_id_list = update_user_id_list()

    for user_id in user_id_list:
        like(user_id)
        # like(user_id, miss_feed_only, record_limit, start_time, end_time) # FIXME: may not work
