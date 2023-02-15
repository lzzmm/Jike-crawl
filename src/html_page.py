# -*- coding:utf8 -*-
# create at: 2023-02-13T21:28:47Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import re
import sys
import json
import requests
import webbrowser
# from tqdm import tqdm


from config import *
from common import *
from utils import *

# TODO: build some templates
#       fix pics
# DONE: function to call

config_show_pic = True

post_data_path = os.path.join(DIR_PATH, "data/posts.json").replace("\\", "/")
coll_data_path = os.path.join(DIR_PATH, "data/collections.json")


post_pic = os.path.join(DIR_PATH, "data/pics/")
coll_pic = os.path.join(DIR_PATH, "data/pics/collections/")

template_post_url = os.path.join(
    DIR_PATH, "data/pages/templates/post.html").replace("\\", "/")
template_like_url = os.path.join(
    DIR_PATH, "data/pages/templates/like.html").replace("\\", "/")
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

    # DONE: rewrite, split base on {%%} and find data by key
    # for key in data:
    #     contents = content.split("{%" + key + "%}")

    #     if len(contents) < 2:
    #         warn("Key", "\"" + key + "\"", "is not used in template.")
    #         continue

    #     for idx, part in enumerate(contents):
    #         if idx == 0:
    #             content = part
    #         else:
    #             content += data[key] + part

    contents = re.split("{%|%}", content)

    content = ""
    for idx, part in enumerate(contents):
        # even
        if not idx & 1:
            content += part

        # odd
        else:
            part = part.strip()  # remove spaces prefix / suffix
            # debug(idx, part)
            if part in data:
                content += data[part]
            else:
                # content += part
                debug("Invalid variable", part)
                pass

    return content


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

    posts = read_multi_json_file(json_data_path)
    # debug(posts[:3])

    post_html = ""

    if data_source is not None:
        data_source = " <code class=\"highlight\">" + data_source + "</code>"
    else:
        data_source = ""

    # TODO: some way to filter posts like topic / create time
    start_index = 0
    end_index = None

    post_content = ""
    for idx, post in enumerate(posts[start_index:end_index]):

        creat_at = datetime.strptime(
            post['createdAt'], "%Y-%m-%dT%X.%fZ").replace(tzinfo=UTC()).astimezone(GMT8())

        post_data = {
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
            "post-link": ""
        }

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
                new_url = ""
                if url["url"].count("jike://page.jk/hashtag/") != 0:
                    new_url = "https://web.okjike.com/topic/" + \
                        url["url"].split("?refTopicId=")[1]
                elif url["url"].count("jike://page.jk/user/") != 0:
                    new_url = "https://web.okjike.com/u/" + \
                        url["url"].split("/user/")[1]
                else:
                    new_url = url["url"]

                new_content = "<a href=\"" + \
                    new_url + "\" target=\"_blank\">" + \
                    url["title"] + "</a>"
                # debug(post_content_old.count(url["originalUrl"]))
                # debug(url["originalUrl"], new_content)
                post_content_old = post_content_old.replace(
                    url["originalUrl"], new_content)

        # post_content_old = post_content_old.replace()
        post_data["post-content"] = post_content_old

        if post["type"] == "REPOST":
            post_data["post-target"] += "<blockquote><div>"

            if "content" in post["target"]:
                if "user" in post["target"] and post["target"]["user"] is not None:
                    post_data["post-target"] += "<div>"
                    post_data["post-target"] += "<h3>" + \
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

        post_data["post-like"] = template_insert(None,
                                                 template_like_url,
                                                 {"like": str(post["likeCount"]),
                                                  "comment": str(post["commentCount"]),
                                                  "share": str(post["repostCount"]),
                                                  "repost": str(post["repostCount"])})

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
        "title": data_source,
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
