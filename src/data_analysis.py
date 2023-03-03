# -*- coding:utf8 -*-
# create at: 2023-01-16T14:39:49Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo

from common import *
from utils import read_multi_json_file, read_json_file, save_json

report_data_path = os.path.join(DIR_PATH, "data/report_data.json")


def summarize_notifications(path):
    x = read_multi_json_file(path)

    users = {}
    users_all = {}
    (
        like_count,
        comment_count,
        like_comment_count,
        reply_count,
        avatar_greet_count,
        followed_count,
        curiosity_count,
        like_count_all,
        comment_count_all,
        like_comment_count_all,
        reply_count_all,
        avatar_greet_count_all,
        followed_count_all,
        curiosity_count_all
    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    # TODO: repeated id

    for node in x:
        user_num = node['actionItem']['usersCount']
        # match & case is in Python 3.10
        if node['type'] == "LIKE_PERSONAL_UPDATE":
            like_count_all += user_num
        elif node['type'] == "COMMENT_PERSONAL_UPDATE":
            comment_count_all += user_num
        elif node['type'] == "LIKE_PERSONAL_UPDATE_COMMENT":
            like_comment_count_all += user_num
        elif node['type'] == "REPLIED_TO_PERSONAL_UPDATE_COMMENT":
            reply_count_all += user_num
        elif node['type'] == "AVATAR_GREET":
            avatar_greet_count_all += user_num
        elif node['type'] == "USER_FOLLOWED" or node['type'] == "USER_SILENT_FOLLOWED":
            followed_count_all += user_num
        elif node['type'] == "CURIOSITY_REPLIED_MY_MENTIONING" or node['type'] == "CURIOSITY_ANSWER_REACTION" or node['type'] == "CURIOSITY_MENTION_ME_ANSWER":
            curiosity_count_all += user_num
        # see README.md->Appendices for more data like CURIOSITY_ANSWER_REACTION

        for user in node['actionItem']['users']:
            if user['username'] not in users_all:
                users_all[user['username']] = {
                    'screenName': user['screenName'],
                    'count': 1
                }
            else:
                users_all[user['username']]['count'] += 1

            if node['type'] not in users_all[user['username']]:
                users_all[user['username']][node['type']] = 1
            else:
                users_all[user['username']][node['type']] += 1

        if datetime.strptime(node['updatedAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8()).year == (CURR_YEAR-1):
            if node['type'] == "LIKE_PERSONAL_UPDATE":
                like_count += user_num
            elif node['type'] == "COMMENT_PERSONAL_UPDATE":
                comment_count += user_num
            elif node['type'] == "LIKE_PERSONAL_UPDATE_COMMENT":
                like_comment_count += user_num
            elif node['type'] == "REPLIED_TO_PERSONAL_UPDATE_COMMENT":
                reply_count += user_num
            elif node['type'] == "AVATAR_GREET":
                avatar_greet_count += user_num
            elif node['type'] == "USER_FOLLOWED" or node['type'] == "USER_SILENT_FOLLOWED":
                followed_count += user_num
            elif node['type'] == "CURIOSITY_REPLIED_MY_MENTIONING" or node['type'] == "CURIOSITY_ANSWER_REACTION" or node['type'] == "CURIOSITY_MENTION_ME_ANSWER":
                curiosity_count += user_num

            for user in node['actionItem']['users']:
                if user['username'] not in users:
                    users[user['username']] = {
                        'screenName': user['screenName'],
                        'count': 1
                    }
                else:
                    users[user['username']]['count'] += 1

    friend_count = len(users)
    interaction_count = like_count + comment_count + like_comment_count + \
        reply_count + avatar_greet_count + curiosity_count

    print("\n")
    print("\033[4;33m%d\033[0m user(s) interacted with you in \033[34mlast year:\033[0m" % friend_count)
    print("\033[4;33m%d\033[0m post-like(s), \033[4;33m%d\033[0m comment(s), \033[4;33m%d\033[0m comment-like(s),\n\033[4;33m%d\033[0m replie(s), \033[4;33m%d\033[0m avatar greet(s), and \033[4;33m%d\033[0m user(s) have followed you.\n" %
          (like_count, comment_count, like_comment_count, reply_count, avatar_greet_count, followed_count))

    most_act_users = sorted(users.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d users\033[0m who interact with you most:" %
          len(most_act_users))

    three_most_interactive = []
    three_most_interactive_time = []
    for user in most_act_users:
        print('\033[33m{0:<20}\033[0m\t\033[33m{1:<3}\033[0m {2:<}'.format(
            user[1]['screenName'], user[1]['count'], "time(s)"), chr(12288))
        three_most_interactive.append(user[1]['screenName'])
        three_most_interactive_time.append(user[1]['count'])

    print("\n")
    print("\033[4;33m%d\033[0m user(s) interacted with you in \033[34mall time:\033[0m" % len(
        users_all))
    print("\033[4;33m%d\033[0m post-like(s), \033[4;33m%d\033[0m comment(s), \033[4;33m%d\033[0m comment-like(s),\n\033[4;33m%d\033[0m repli(es), \033[4;33m%d\033[0m avatar greet(s), and \033[4;33m%d\033[0m user(s) have followed you.\n" %
          (like_count_all, comment_count_all, like_comment_count_all, reply_count_all, avatar_greet_count_all, followed_count_all))

    most_act_users = sorted(users_all.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d users\033[0m who interact with you most:" %
          len(most_act_users))

    for user in most_act_users:
        print('\033[33m{0:<20}\033[0m\t\033[33m{1:<3}\033[0m {2:<}'.format(
            user[1]['screenName'], user[1]['count'], "time(s)"), chr(12288))

    print("")
    print("Your likes and comments are \033[4mNOT\033[0m included.")
    CURR_TIME = datetime.now(GMT8())
    print("Generated at", CURR_TIME)
    print("")

    json_data = read_json_file(report_data_path)

    # json_data["year"] = CURR_YEAR-1
    # json_data["total_posts"] = sum(post_count)
    # json_data["total_likes"] = like_count_all
    json_data["likes"] = like_count
    json_data["replies"] = reply_count
    json_data["friends"] = friend_count
    json_data["interactions"] = interaction_count
    json_data["three_most_interactive"] = str(three_most_interactive[:3])
    json_data["interaction_count"] = str(three_most_interactive_time[:3])

    save_json(json_data, report_data_path, 'w', 2)


def summarize_posts(path):
    x = read_multi_json_file(path)

    post_count = [0] * (CURR_YEAR-BASE_YEAR + 1)
    topics = {}
    topics_all = {}
    (
        like_count,
        comment_count,
        repost_count,
        share_count,
        pic_count,
        like_count_all,
        comment_count_all,
        repost_count_all,
        share_count_all,
        pic_count_all
    ) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    daily_post_count = [0] * 366

    for node in x:
        create_at = datetime.strptime(
            node['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
        post_count[create_at.year - BASE_YEAR] += 1

        like_count_all += node['likeCount']
        comment_count_all += node['commentCount']
        repost_count_all += node['repostCount']
        share_count_all += node['shareCount']
        pic_count_all += len(node['pictures'])

        if 'topic' in node and node['topic'] != None:
            if node['topic']['id'] not in topics_all:
                topics_all[node['topic']['id']] = {
                    'content': node['topic']['content'],
                    'count': 1
                }
            else:
                topics_all[node['topic']['id']]['count'] += 1

        if create_at.year == (CURR_YEAR-1):

            like_count += node['likeCount']
            comment_count += node['commentCount']
            repost_count += node['repostCount']
            share_count += node['shareCount']
            pic_count += len(node['pictures'])
            first_day = datetime(create_at.year, 1, 1, tzinfo=GMT8())
            days_of_year = create_at - first_day
            daily_post_count[days_of_year.days] += 1

            if 'topic' in node and node['topic'] != None:
                if node['topic']['id'] not in topics:
                    topics[node['topic']['id']] = {
                        'content': node['topic']['content'],
                        'count': 1
                    }
                else:
                    topics[node['topic']['id']]['count'] += 1
            # TODO: post time in a day, priority: low

    # print(daily_post_count)

    print("\n")
    print("In \033[34m%d\033[0m:" % (CURR_YEAR-1))
    print("You've posted \033[4;33m", post_count[CURR_YEAR-BASE_YEAR-1],
          "\033[0m post(s) including \033[4;33m", pic_count, "\033[0m picture(s)", sep='')

    if post_count[CURR_YEAR-BASE_YEAR-2] != 0:
        rate = post_count[CURR_YEAR-BASE_YEAR-1] * \
            100 / post_count[CURR_YEAR-BASE_YEAR-2]
        print("Which is \033[4;33m", "%.2f" %
              (rate), "%\033[0m of last year's", sep='')

    print("Received \033[4;33m%d\033[0m like(s) and \033[4;33m%d\033[0m comment(s)" % (
        like_count, comment_count))
    print("Get \033[4;33m%d\033[0m repost(s) and \033[4;33m%d\033[0m share(s)\n" % (
        repost_count, share_count))

    most_topics = sorted(topics.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d topics\033[0m you're most interested in:" %
          len(most_topics))

    three_most_topic = []
    three_most_topic_post = []
    for topic in most_topics:
        print('\033[33m{0:<12}\033[0m \t==>\t\033[33m{1:>3}\033[0m {2:>}'.format(
            topic[1]['content'], topic[1]['count'], "post(s)"), chr(12288))
        three_most_topic.append(topic[1]['content'])
        three_most_topic_post.append(topic[1]['count'])

    print("\n")

    # -------------------------------------------

    print("In \033[34mall time\033[0m:")

    print("You've posted \033[4;33m", sum(post_count), "\033[0m post(s) including \033[4;33m",
          pic_count_all, "\033[0m picture(s)", sep='')
    print("Received \033[4;33m%d\033[0m like(s) and \033[4;33m%d\033[0m comment(s)" % (
        like_count, comment_count))
    print("Get \033[4;33m%d\033[0m repost(s) and \033[4;33m%d\033[0m share(s)\n" % (
        repost_count, share_count))

    most_topics = sorted(topics_all.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d topics\033[0m you're most interested in:" %
          len(most_topics))

    for topic in most_topics:
        print('\033[33m{0:<12}\033[0m \t==>\t\033[33m{1:>3}\033[0m {2:>}'.format(
            topic[1]['content'], topic[1]['count'], "post(s)"), chr(12288))

    print("")
    print(
        "Number of post(s) you've post \033[34m%d-%d\033[0m:\033[33m" % (BASE_YEAR, CURR_YEAR))
    print(post_count, "\033[0m\n")

    print("Deleted data is \033[4mNOT\033[0m included.")
    print("Your likes and comments are included.")
    CURR_TIME = datetime.now(GMT8())
    print("Generated at", CURR_TIME)
    print("")

    json_data = read_json_file(report_data_path)

    json_data["year"] = CURR_YEAR-1
    json_data["total_posts"] = sum(post_count)
    json_data["total_likes"] = like_count_all
    json_data["posts"] = post_count[CURR_YEAR-BASE_YEAR-1]
    json_data["three_most_topic"] = str(three_most_topic[:3])
    json_data["post_topic"] = str(three_most_topic_post[:3])
    json_data["daily_post_count"] = str(daily_post_count)

    save_json(json_data, report_data_path, 'w', 2)


if __name__ == "__main__":
    noti_path = os.path.join(DIR_PATH, "data/notifications.json")
    post_path = os.path.join(DIR_PATH, "data/posts.json")
    summarize_posts(post_path)
    summarize_notifications(noti_path)
