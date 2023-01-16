import os
import sys
import json
import requests
from datetime import datetime, timedelta, tzinfo

dir_path = os.path.dirname(os.path.dirname(__file__))

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return 'UTC'

    def tzoffset(self, dt):
        return ZERO


class GMT8(tzinfo):
    def utcoffset(self, dt):
        return HOUR * 8

    def tzname(self, dt):
        return 'GMT+8'

    def dst(self, dt):
        return ZERO


cur_year = datetime.now(GMT8()).year
base_year = 2016


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


def read_file(path):
    with open(path, 'r', encoding="utf8") as f:
        count = 0
        x = []
        line = f.readline()
        while (line):
            x.append(json.loads(line))
            count += 1
            line = f.readline()
            # if count == 100:
            #     break
        print("Read", count, "line(s) from", path)
        return x


def summarize_notifications(path):
    x = read_file(path)

    users = {}
    users_all = {}
    like_count = comment_count = like_comment_count = reply_count = avatar_greet_count = followed_count = 0
    like_count_all = comment_count_all = like_comment_count_all = reply_count_all = avatar_greet_count_all = followed_count_all = 0
    for i in x:

        user_num = i['actionItem']['usersCount']
        # match & case is in Python 3.10
        if i['type'] == "LIKE_PERSONAL_UPDATE":
            like_count_all += user_num
            # with open('like_count_all.txt', 'a', encoding="utf8") as f:
            #     f.write(str(like_count_all) + "\n")
        elif i['type'] == "COMMENT_PERSONAL_UPDATE":
            comment_count_all += user_num
        elif i['type'] == "LIKE_PERSONAL_UPDATE_COMMENT":
            like_comment_count_all += user_num
        elif i['type'] == "REPLIED_TO_PERSONAL_UPDATE_COMMENT":
            reply_count_all += user_num
        elif i['type'] == "AVATAR_GREET":
            avatar_greet_count_all += user_num
        elif i['type'] == "USER_FOLLOWED" or i['type'] == "USER_SILENT_FOLLOWED":
            followed_count_all += user_num
        # see README.md->Appendices for more data like CURIOSITY_ANSWER_REACTION

        for user in i['actionItem']['users']:
            # print(user['username'])
            if user['username'] not in users_all:
                users_all[user['username']] = {
                    'screenName': user['screenName'],
                    'count': 1
                }
            else:
                users_all[user['username']]['count'] += 1
            if i['type'] not in users_all[user['username']]:
                users_all[user['username']][i['type']] = 1
            else:
                users_all[user['username']][i['type']] += 1

        if datetime.strptime(i['updatedAt'], "%Y-%m-%dT%X.%fZ").astimezone(GMT8()).year == (cur_year-1):
            if i['type'] == "LIKE_PERSONAL_UPDATE":
                like_count += user_num
            elif i['type'] == "COMMENT_PERSONAL_UPDATE":
                comment_count += user_num
            elif i['type'] == "LIKE_PERSONAL_UPDATE_COMMENT":
                like_comment_count += user_num
            elif i['type'] == "REPLIED_TO_PERSONAL_UPDATE_COMMENT":
                reply_count += user_num
            elif i['type'] == "AVATAR_GREET":
                avatar_greet_count += user_num
            elif i['type'] == "USER_FOLLOWED" or i['type'] == "USER_SILENT_FOLLOWED":
                followed_count += user_num

            for user in i['actionItem']['users']:
                # print(user['username'])
                if user['username'] not in users:
                    users[user['username']] = {
                        'screenName': user['screenName'],
                        'count': 1
                    }
                else:
                    users[user['username']]['count'] += 1

    print("\n")
    print("\033[4;33m%d\033[0m users interacted with you in \033[34mlast year:\033[0m" % len(users))
    print("\033[4;33m%d\033[0m post-likes, \033[4;33m%d\033[0m comments, \033[4;33m%d\033[0m comment-likes,\n\033[4;33m%d\033[0m replies, \033[4;33m%d\033[0m avatar greets, and \033[4;33m%d\033[0m users have followed you.\n" %
          (like_count, comment_count, like_comment_count, reply_count, avatar_greet_count, followed_count))

    most_act_users = sorted(users.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d users\033[0m users who interact with you most:" %
          len(most_act_users))
    for user in most_act_users:
        print('\033[33m{0:<20}\033[0m\t\033[33m{1:<3}\033[0m {2:<}'.format(
            user[1]['screenName'], user[1]['count'], "time(s)"), chr(12288))

    print("\n")
    print("\033[4;33m%d\033[0m users interacted with you in \033[34mall time:\033[0m" % len(
        users_all))
    print("\033[4;33m%d\033[0m post-likes, \033[4;33m%d\033[0m comments, \033[4;33m%d\033[0m comment-likes,\n\033[4;33m%d\033[0m replies, \033[4;33m%d\033[0m avatar greets, and \033[4;33m%d\033[0m users have followed you.\n" %
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
    print("Generated at", datetime.now(GMT8()))
    print("")


def summarize_posts(path):
    x = read_file(path)

    post_count = [0]*(cur_year-base_year+1)
    topics = {}
    topics_all = {}
    like_count = comment_count = repost_count = share_count = pic_count = 0
    like_count_all = comment_count_all = repost_count_all = share_count_all = pic_count_all = 0
    # print(datetime.strptime(x[0]['createdAt'], "%Y-%m-%dT%X.%fZ")) # '%Y-%m-%dT%H:%M:%S.%fZ'
    for i in x:

        post_count[datetime.strptime(
            i['createdAt'], "%Y-%m-%dT%X.%fZ").astimezone(GMT8()).year - base_year] += 1

        like_count_all += i['likeCount']
        # with open('like_count_all.txt', 'a', encoding="utf8") as f:
        #     f.write(str(like_count_all) + "\n")
        comment_count_all += i['commentCount']
        repost_count_all += i['repostCount']
        share_count_all += i['shareCount']
        pic_count_all += len(i['pictures'])
        if 'topic' in i and i['topic'] != None:
            if i['topic']['id'] not in topics_all:
                topics_all[i['topic']['id']] = {
                    'content': i['topic']['content'],
                    'count': 1
                }
            else:
                topics_all[i['topic']['id']]['count'] += 1
        if datetime.strptime(i['createdAt'], "%Y-%m-%dT%X.%fZ").astimezone(GMT8()).year == (cur_year-1):
            like_count += i['likeCount']
            comment_count += i['commentCount']
            repost_count += i['repostCount']
            share_count += i['shareCount']
            pic_count += len(i['pictures'])
            if 'topic' in i and i['topic'] != None:
                if i['topic']['id'] not in topics:
                    topics[i['topic']['id']] = {
                        'content': i['topic']['content'],
                        'count': 1
                    }
                else:
                    topics[i['topic']['id']]['count'] += 1
            # TODO: post time in a day
            # TODO: interact most num people num interacts

    print("\n")
    print("In \033[34m%d\033[0m:" % (cur_year-1))
    print("You've posted \033[4;33m", post_count[cur_year-base_year-1],
          "\033[0m post(s) including \033[4;33m", pic_count, "\033[0m picture(s)", sep='')
    if post_count[cur_year-base_year-2] != 0:
        rate = post_count[cur_year-base_year-1] * \
            100 / post_count[cur_year-base_year-2]
        print("Which is \033[4;33m", "%.2f" %
              (rate), "%\033[0m of last year's", sep='')
    print("Received\033[33m", like_count,
          "\033[0mlike(s) and\033[33m", comment_count, "\033[0mcomment(s)")
    print("Get\033[33m", repost_count, "\033[0mrepost(s) and\033[33m",
          share_count, "\033[0mshare(s)\n")

    most_topics = sorted(topics.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d topics\033[0m you're most interested in:" %
          len(most_topics))
    for topic in most_topics:
        print('\033[33m{0:<12}\033[0m \t==>\t\033[33m{1:>3}\033[0m {2:>}'.format(
            topic[1]['content'], topic[1]['count'], "post(s)"), chr(12288))

    print("\n")

    # -------------------------------------------

    print("In \033[34mall time\033[0m:")
    print("You've posted \033[4;33m", sum(post_count), "\033[0m post(s) including \033[4;33m",
          pic_count_all, "\033[0m picture(s)", sep='')
    print("Received\033[33m", like_count_all, "\033[0mlike(s) and\033[33m",
          comment_count_all, "\033[0mcomment(s)")
    print("Get\033[33m", repost_count_all, "\033[0mrepost(s) and\033[33m",
          share_count_all, "\033[0mshare(s)\n")

    most_topics = sorted(topics_all.items(), key=lambda x: x[1]['count'],  reverse=True)[
        :10]  # could change
    print("\033[4;33m%d topics\033[0m you're most interested in:" %
          len(most_topics))
    for topic in most_topics:
        print('\033[33m{0:<12}\033[0m \t==>\t\033[33m{1:>3}\033[0m {2:>}'.format(
            topic[1]['content'], topic[1]['count'], "post(s)"), chr(12288))

    print("")
    print(
        "Number of post(s) you've post \033[34m2016-%d\033[0m:\033[33m" % cur_year)
    print(post_count, "\033[0m\n")

    print("Deleted data is \033[4mNOT\033[0m included.")
    print("Your likes and comments are included.")
    print("Generated at", datetime.now(GMT8()))
    print("")


if __name__ == "__main__":
    noti_path = os.path.join(dir_path, "data/notifications.json")
    post_path = os.path.join(dir_path, "data/posts.json")
    summarize_posts(post_path)
    summarize_notifications(noti_path)
