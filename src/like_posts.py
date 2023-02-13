# -*- coding:utf8 -*-
# create at: 2023-02-07T16:02:19Z+08:00
# author:    lzzmm<2313681700@qq.com>


from utils import *
from config import *


def like(user_ids: list, miss_feed_only=False, record_limit=5, start_time=BASE_TIME, end_time=CURR_TIME):

    for user_id in user_ids:

        crawl_posts_fn(user_id,
                       proc_node_fn,
                       PAYLOAD_LIKE,
                       miss_feed_only=miss_feed_only,
                       user_id_list=user_ids,
                       record_count_limit=record_limit,
                       start_time=start_time,
                       end_time=end_time)

        if miss_feed_only == True:
            break


def unlike(user_ids: list, miss_feed_only=False, record_limit=5, start_time=BASE_TIME, end_time=CURR_TIME):

    for user_id in user_ids:

        crawl_posts_fn(user_id,
                       proc_node_fn,
                       PAYLOAD_UNLIKE,
                       miss_feed_only=miss_feed_only,
                       user_id_list=user_ids,
                       record_count_limit=record_limit, start_time=start_time,
                       end_time=end_time)

        if miss_feed_only == True:
            break


def hide():
    # TODO: API is not graphgl
    x = op_post(PAYLOAD_HIDE)
    debug(x)


# DONE: search by name, multi user supports
# TODO: record last post, and reconstruct functions
#       threading
#       miss_feed_only haven't tested yet
#       fishball: 或者把好友列表取出来放文件里
#                 FAILED: 暂时找不到新版 getFollowingList 接口


def load_following_list(path_from: str = os.path.join(DIR_PATH, "config/user_list_temp.txt"), path_to: str = os.path.join(DIR_PATH, "config/user_id_list.txt")):
    list = read_list_file(path_from)
    save_list([user.split()[1] for user in list], path_to)


if __name__ == "__main__":
    start_time = CURR_TIME - timedelta(days=1)  # datetime
    end_time = CURR_TIME    # datetime
    record_limit = 5        # int or None
    # like too many posts from a user in a short time
    # may make that user feel troubled
    miss_feed_only = True

    # crawl_following()  # haven't done yet # DONE: see main.ipynb

    # user_id_list = read_list_file(os.path.join(
    #     DIR_PATH, "config/user_id_list.txt"))

    # call if you have changed "config/user_name_list.txt"
    user_id_list = update_user_id_list()

    # for user_id in user_id_list:
    like(user_id_list)

    # like(user_id_list, miss_feed_only, record_limit, start_time, end_time)
