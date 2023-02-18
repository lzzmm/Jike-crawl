# -*- coding:utf8 -*-
# create at: 2023-02-13T21:28:47Z+08:00
# author:    lzzmm<2313681700@qq.com>
# comment:   This file contains functions for creating HTML pages from json data

import os
import re
import sys
import json
import requests
import webbrowser
from tqdm import tqdm


from config import *
from common import *
from utils import *

# TODO: build some templates
#       fix pics
# DONE: function to call

config_show_pic = True
END_INDEX = None

post_data_path = os.path.join(DIR_PATH, "data/posts.json").replace("\\", "/")
coll_data_path = os.path.join(DIR_PATH, "data/collections.json")
comm_dir_path = os.path.join(DIR_PATH, "data/comments/")


post_pic = os.path.join(DIR_PATH, "data/pics/posts/")
coll_pic = os.path.join(DIR_PATH, "data/pics/collections/")

template_post_url = os.path.join(
    DIR_PATH, "data/pages/templates/post.html").replace("\\", "/")
template_like_url = os.path.join(
    DIR_PATH, "data/pages/templates/like.html").replace("\\", "/")
template_comment_url = os.path.join(
    DIR_PATH, "data/pages/templates/comment.html").replace("\\", "/")
template_url = os.path.join(
    DIR_PATH, "data/pages/templates/template.html").replace("\\", "/")

post_html_url = os.path.join(
    DIR_PATH, "data/pages/posts.html").replace("\\", "/")
coll_html_url = os.path.join(
    DIR_PATH, "data/pages/collections.html").replace("\\", "/")


def template_insert(template_str: str, template_path: str, data: dict) -> str:
    """
    Insert data into template
    ---
    Return:
        inserted string
    """
    content = template_str

    if template_str is None:
        with open(template_path, "r", encoding="utf8") as f:
            content = f.read()

    contents = re.split("{%|%}", content)

    content = ""
    pass_else_stack = [False]
    branch_ctrl_stack = [True]
    branch_depth = 0
    for idx, part in enumerate(contents):
        # even
        if idx & 1 == 0:
            if branch_ctrl_stack[branch_depth] == True:
                content += part

        # odd
        else:
            # debug(part)
            part = part.strip()  # remove spaces prefix / suffix
            parts = part.split(' ')
            # debug("part:", part)

            b_num_cmp = True
            # DONE: support nesting
            if len(parts) >= 2:

                key_idx = 1
                b_key = True

                if parts[key_idx] == "not":
                    key_idx += 1
                    b_key = False

                # num
                if type(parts[key_idx]) == type(0):
                    ...

                # bool
                if type(parts[key_idx]) == type(True):
                    ...

                # TODO:
                # bool
                elif parts[key_idx] in data and type(data[parts[key_idx]]) == type(True):
                    b_num_cmp = data[parts[key_idx]]

                # if not a == b, key_idx: 2, len: 5
                if len(parts) == key_idx + 3:
                    symbol_list_1 = ["\"", "\'", "("]
                    symbol_list_2 = ["[", "{", "("]

                    # string
                    if parts[key_idx+2][0] in symbol_list_1:
                        parts[key_idx+2] = parts[key_idx+2][1:-1]

                    # template var
                    elif parts[key_idx+2][0] in symbol_list_2:
                        parts[key_idx+2] = data[parts[key_idx+2][1:-1]]

                    # numeric (int only)
                    elif parts[key_idx+2].isnumeric() == True:
                        if parts[key_idx] in data and type(data[parts[key_idx]]) == type(0):
                            parts[key_idx+2] = int(parts[key_idx+2])

                            if parts[key_idx+1] == "==":
                                if data[parts[key_idx]] != parts[key_idx+2]:
                                    # b_key = not b_key
                                    b_num_cmp = False
                                # info(data[parts[key_idx]], b_num_cmp)

                            elif parts[key_idx+1] == ">":
                                # info(data[parts[key_idx]])
                                if data[parts[key_idx]] <= parts[key_idx+2]:
                                    # b_key = not b_key
                                    b_num_cmp = False

                                # info(b_num_cmp)

                            elif parts[key_idx+1] == ">=":
                                if data[parts[key_idx]] < parts[key_idx+2]:
                                    # b_key = not b_key
                                    b_num_cmp = False

                            elif parts[key_idx+1] == "<":
                                if data[parts[key_idx]] >= parts[key_idx+2]:
                                    b_num_cmp = False
                                    # b_key = not b_key

                            elif parts[key_idx+1] == "<=":
                                if data[parts[key_idx]] > parts[key_idx+2]:
                                    b_num_cmp = False
                                    # b_key = not b_key

                        else:
                            b_key = not b_key

                    else:
                        b_key = not b_key

                if parts[0] == "if":
                    # info("if start", branch_ctrl_stack)
                    
                    if branch_ctrl_stack[branch_depth] == True:
                        if parts[key_idx] not in data or b_num_cmp == False:  # FIXME: bug == 0
                            # info("b_key", b_key)
                            branch_ctrl_stack.append(not b_key)
                        else:
                            # info("b_key", b_key)
                            branch_ctrl_stack.append(b_key)

                    else:
                        branch_ctrl_stack.append(False)

                    branch_depth += 1

                    pass_else_stack.append(branch_ctrl_stack[branch_depth])

                    # info(parts, branch_ctrl_stack)
                    # info(pass_else_stack, parts, branch_depth, branch_ctrl_stack)

                elif parts[0] == "elif":
                    if branch_ctrl_stack[branch_depth - 1] == True:
                        if pass_else_stack[branch_depth] == True:
                            # info("elif pass")
                            branch_ctrl_stack[branch_depth] = False
                        else:
                            if parts[key_idx] not in data or b_num_cmp == False:
                                # info("elif ", not b_key)
                                branch_ctrl_stack[branch_depth] = not b_key
                            else:
                                # info("elif ", b_key)
                                branch_ctrl_stack[branch_depth] = b_key

                            if branch_ctrl_stack[branch_depth] == True:
                                pass_else_stack[branch_depth] = True
                    else:
                        branch_ctrl_stack[branch_depth] = False
                        pass_else_stack[branch_depth] = True
                    # info(parts, b_key, branch_ctrl_stack)
                    # info(pass_else_stack, parts, branch_depth, branch_ctrl_stack)
                    ...
            else:
                if part == "endif":

                    del branch_ctrl_stack[branch_depth]
                    del pass_else_stack[branch_depth]
                    branch_depth -= 1

                    # debug("endif", branch_depth, branch_ctrl_stack)

                elif part == "else":
                    if branch_ctrl_stack[branch_depth - 1] == True:
                        if pass_else_stack[branch_depth] == True:
                            branch_ctrl_stack[branch_depth] = False
                        else:
                            branch_ctrl_stack[branch_depth] = True
                    else:
                        branch_ctrl_stack[branch_depth] = False
                        pass_else_stack[branch_depth] = True

                    # debug("else", branch_ctrl_stack)

                elif branch_ctrl_stack[branch_depth] == False:
                    continue

                elif part in data:
                    # # debug("part in data", data[part])
                    content += str(data[part])

                else:
                    # content += part
                    debug("Invalid variable", part)

    return content


def urls_in_text(url: dict) -> str:
    if "url" not in url:
        return ""

    new_url = ""
    # info(url)
    if url["url"].count("jike://page.jk/hashtag/") != 0:
        new_url = url["url"].split("?refTopicId=")
        if len(new_url) > 1:
            new_url = "https://web.okjike.com/topic/" + new_url[1]
        else:
            new_url = url["url"]
    elif url["url"].count("jike://page.jk/user/") != 0:
        new_url = url["url"].split("/user/")
        if len(new_url) > 1:
            new_url = "https://web.okjike.com/u/" + new_url[1]
        else:
            new_url = url["url"]
    else:
        new_url = url["url"]

    new_content = "<a href=\"" + \
        new_url + "\" target=\"_blank\">" + \
        url["title"] + "</a>"

    # info(new_content)
    return new_content


def post_page(json_data_path: str = post_data_path, html_path: str = post_html_url, pic_path: str = post_pic, show_user: bool = False, data_source: str = None, template_path: str = template_url) -> None:

    content = ""
    copyright_user = {
        "user_id": "",
        "user_name": "",
        "start_year": BASE_YEAR,
        "end_year": CURR_YEAR,
        "b_has_start_year": False,
        "b_show": True
    }

    with open(template_path, "r", encoding="utf8") as f:
        content = f.read()
        # debug(content)

    posts = read_multi_json_file(json_data_path, print_done=False)

    title = ""

    if data_source is not None:
        title += data_source + " | "
        data_source = " <code class=\"highlight\">" + data_source + "</code>"
    else:
        data_source = ""

    title += "JIKE Archive"

    # TODO: some way to filter posts like topic / create time
    start_index = 0
    end_index = END_INDEX

    post_content = ""
    for idx, post in tqdm(enumerate(posts[start_index:end_index]), total=len(posts) if end_index is None else end_index - start_index):
        # info(post["id"])

        creat_at = datetime.strptime(
            post['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())
        post_id = post['id']
        # info(post_id)

        post_data = {
            "post_id": post_id,
            "post-idx": str(idx + start_index),
            "user-name": "",
            "user-bio": "",
            "create-time": str(creat_at.__format__("%Y-%m-%d %X (%Z)")),
            "post-topic-content": "",
            "post-content": "",
            "post-pics": "",
            "post-target": "",
            "post-linkInfo": "",
            "post-like": "",
            "post-link": "",
            "post-comments": ""
        }

        # TODO: write template

        if copyright_user["b_show"] == True:
            if "user" in post and post["user"] is not None:
                if idx == 0:
                    copyright_user["user_name"] = post["user"]["screenName"]
                    copyright_user["user_id"] = post["user"]["username"]
                    copyright_user["end_year"] = creat_at.year
                else:
                    if copyright_user["user_id"] != post["user"]["username"]:
                        copyright_user["b_show"] = False
                    if creat_at.year != copyright_user["end_year"]:
                        copyright_user["b_has_start_year"] = True
                        copyright_user["start_year"] = creat_at.year

        if show_user and "user" in post and post["user"] is not None:
            if "screenName" in post["user"]:
                post_data["user-name"] = post["user"]["screenName"]

            if "briefIntro" in post["user"] and post["user"]["briefIntro"] != "":
                post_data["user-bio"] = "<div class=\"user-bio\">" + post["user"]["briefIntro"].replace(
                    "\n", "<br/>") + "</div>"

        if "topic" in post and post["topic"] is not None:
            post_data["post-topic-content"] = "<h3><code class=\"topic\">"
            post_data["post-topic-content"] += post["topic"]["content"]
            post_data["post-topic-content"] += "</code></h3>"

        if config_show_pic == True:
            post_pic_path = os.path.join(pic_path, post["id"])
            if os.path.isdir(post_pic_path):
                for pic in post["pictures"]:
                    pic = os.path.join(post_pic_path, pic["picUrl"].split("?")[
                        0].split("/")[-1])
                    if os.path.isfile(pic):
                        post_data["post-pics"] += "<div class=\"cropped\"><a href=" + pic + \
                            " target=\"_blank\" title=\"open picture\">"
                        post_data["post-pics"] += "<img src=\"" + \
                            pic + "\" alt=\"" + pic + "\" ></a></div>"

        post_content_old: str = post["content"].replace("\n", "<br/>")
        if "urlsInText" in post:
            for url in post["urlsInText"]:
                post_content_old = post_content_old.replace(
                    url["originalUrl"], urls_in_text(url))

        post_data["post-content"] = post_content_old

        if post["type"] == "REPOST":
            post_data["post-target"] += "<blockquote><div>"

            if "content" in post["target"]:
                if "user" in post["target"] and post["target"]["user"] is not None:
                    post_data["post-target"] += "<div>"
                    post_data["post-target"] += "<h3 class=\"\">" + \
                        post["target"]["user"]["screenName"] + "</h3>"
                    post_data["post-target"] += "</div>"
                if "topic" in post["target"] and post["target"]["topic"] is not None:
                    post_data["post-target"] += "<div>"
                    post_data["post-target"] += "<h4><code class=\"topic\">" + \
                        post["target"]["topic"]["content"] + "</code></h4>"
                    post_data["post-target"] += "</div>"
                post_data["post-target"] += post["target"]["content"].replace(
                    "\n", "<br/>")

                post_data["post-target"] += "<br/><div><br/><code class=\"highlight\">"
                post_data["post-target"] += post["target"]["type"] + "</code><code><a href=\"https://web.okjike.com/originalPost/" + \
                    post["target"]["id"] + "\" target=\"_blank\" title=\"open in Jike\">" + \
                    "🔗" + post["target"]["id"]
                post_data["post-target"] += "</a></code></div><br/>"

            elif "status" in post["target"]:
                post_data["post-target"] += "<code class=\"highlight\">"
                post_data["post-target"] += post["target"]["status"]
                post_data["post-target"] += "</code>"

            post_data["post-target"] += "</div></blockquote>"

        if "linkInfo" in post and post["linkInfo"] is not None:
            # post_data["post-linkInfo"] += "<div>"
            post_data["post-linkInfo"] += "<a href=\"" + post["linkInfo"]["linkUrl"] + \
                "\" target=\"_blank\" title=\"open link\">🔗" + \
                post["linkInfo"]["title"] + "</a><br/>"

        comm_len = 0
        comm_data_path = os.path.join(comm_dir_path, post_id + ".json")
        if os.path.isfile(comm_data_path) == True:

            comments = read_multi_json_file(comm_data_path, print_done=False)

            comm_len = len(comments)
            for comm_idx, comment in enumerate(comments):
                b_container_start = True if comm_idx == 0 else False
                b_container_end = True if comm_idx == comm_len - 1 else False

                hot_replies = ""
                for hrp_idx, hrp in enumerate(comment["hotReplies"]):

                    pics_link = ""
                    for pic in hrp["pictures"]:
                        # TODO: if downloaded
                        comm_pic_path = os.path.join(pic_path, post["id"])
                        pics_link += "<br /><a href=\"" + \
                            pic["picUrl"] + "\" target=\"_blank\">🖼️ " + \
                            pic["format"] + "</a>"

                    hrp_content: str = hrp["content"].replace("\n", "<br/>")
                    if "urlsInText" in hrp and hrp["urlsInText"] is not None:
                        for url in hrp["urlsInText"]:
                            hrp_content = hrp_content.replace(
                                url["originalUrl"], urls_in_text(url))

                    hot_replies += template_insert(None, template_comment_url, {"user-name": hrp["user"]["screenName"], "create-time": datetime.strptime(
                        hrp["createdAt"], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8()).__format__("%Y-%m-%d %X %Z"), "content": hrp_content + pics_link, "to-user-name": hrp["replyToComment"]["user"]["screenName"], "level": hrp["level"]})

                pics_link = ""
                for pic in comment["pictures"]:
                    pics_link += "<br /><a href=\"" + \
                        pic["picUrl"] + "\" target=\"_blank\">🖼️ " + \
                        pic["format"] + "</a>"

                comment_content: str = comment["content"].replace(
                    "\n", "<br/>")
                if "urlsInText" in comment and comment["urlsInText"] is not None:
                    for url in comment["urlsInText"]:
                        comment_content = comment_content.replace(
                            url["originalUrl"], urls_in_text(url))

                comm_data = {"container-start": b_container_start,
                             "container-end": b_container_end,
                             "num-comment": comm_len,
                             "post-idx": str(idx + start_index),
                             "user-name": comment["user"]["screenName"],
                             "create-time": datetime.strptime(comment["createdAt"], "%Y-%m-%dT%X.%fZ").
                             replace(tzinfo=UTC()).astimezone(
                                 GMT8()).__format__("%Y-%m-%d %X %Z"),
                             "content": comment_content + pics_link,
                             "level": comment["level"],
                             "hot-replies": hot_replies if hot_replies != "" else False}

                post_data["post-comments"] += template_insert(
                    None, template_comment_url, comm_data)

        else:
            post_data["post-comments"] = template_insert(
                None, template_comment_url, {"container-start": True, "container-end": True, "num-comment": comm_len, "post-idx": str(idx + start_index)})

        post_data["post-like"] = template_insert(None,
                                                 template_like_url,
                                                 {"like": str(post["likeCount"]),
                                                  "comment": str(post["commentCount"]),
                                                  "share": str(post["repostCount"]),
                                                  "repost": str(post["repostCount"]),
                                                  "post-idx": str(idx + start_index)})

        post_data["post-link"] += post["type"] + "</code><code><a href=\"https://web.okjike.com/originalPost/" + \
            post["id"] + "\" target=\"_blank\" title=\"open in Jike\">" + \
            "🔗" + post["id"] + "</a></code></div><br/>"

        post_content += template_insert(None, template_post_url, post_data)

    copyright_content = ""

    if copyright_user["b_show"] == True:
        copyright_content += "<br /><br /><text class=\"copyright\">&copy;<code>"
        if copyright_user["b_has_start_year"] == True:
            copyright_content += str(copyright_user["start_year"]) + "-"
        copyright_content += str(copyright_user["end_year"]) + "</code> "
        copyright_content += "<a href=\"https://web.okjike.com/u/" + \
            copyright_user["user_id"] + "\" target=\"_blank\">"
        copyright_content += copyright_user["user_name"]
        copyright_content += "</a></text>"

    data = {
        "title": title,
        "data-source": data_source,
        "curr-time": str(datetime.now(GMT8())),
        "post": post_content,
        "post-count": str(idx+1),
        "post-data-url": json_data_path.replace("\\", "/"),
        "footer-like": template_insert(None,
                                       template_like_url,
                                       {"like": "like",
                                        "comment": "comment",
                                        "share": "share",
                                        "repost": "repost"}),
        "copyright": copyright_content
    }

    content = template_insert(None, template_url, data)

    with open(html_path, "w", encoding="utf8") as f:
        f.write(content)


if __name__ == "__main__":

    post_page(data_source="User Posts")
    webbrowser.open_new_tab(post_html_url)
    done(post_html_url, "opened.")
    post_page(coll_data_path, coll_html_url,
              coll_pic, True, "User Collections")
    webbrowser.open_new_tab(coll_html_url)
    done(coll_html_url, "opened.")
