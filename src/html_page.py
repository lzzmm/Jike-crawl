# -*- coding:utf8 -*-
# create at: 2023-02-13T21:28:47Z+08:00
# author:    lzzmm<2313681700@qq.com>

import os
import sys
import json
import requests
import webbrowser

from config import *
from common import *
from utils import *

# TODO: build some templates
#       fix pics
# DONE: function to call

post_data_path = os.path.join(DIR_PATH, "data/posts.json").replace("\\", "/")
template_url = os.path.join(DIR_PATH, "data/pages/template.html").replace("\\", "/")
url = os.path.join(DIR_PATH, "data/pages/posts.html").replace("\\", "/")


def template_insert(template_path: str, data: dict) -> str:
    # TODO: rewrite, split base on {%%} and find data by key

    content = ""

    with open(template_path, "r", encoding="utf8") as f:
        content = f.read()

    for key in data:
        contents = content.split("{%" + key + "%}")

        if len(contents) < 2:
            warn("Key", "\"" + key + "\"", "is not used in template.")
            continue

        for idx, part in enumerate(contents):
            if idx == 0:
                content = part
            else:
                content += data[key] + part

    return content


def post_page(post_data_path: str = post_data_path, template_path: str = template_url) -> None:


    content = ""

    with open(template_url, "r", encoding="utf8") as f:
        content = f.read()
        # debug(content)

    posts = read_multi_json_file(post_data_path)
    # debug(posts[:3])

    post_data = ""

    # TODO: some way to filter posts like topic / create time
    start_index = 0
    end_index = None

    for idx, post in enumerate(posts[start_index:end_index]):
        post_data += "<div id=\"post-" + \
            str(idx + start_index) + "\"class=\"post\"><h2><code>"
        post_data += "#" + str(idx + start_index) + " "
        post_data += str(datetime.strptime(post['createdAt'], "%Y-%m-%dT%X.%fZ").replace(
            tzinfo=UTC()).astimezone(GMT8()).__format__("%Y-%m-%d %X (%Z)"))
        post_data += "</code></h2>"

        if "topic" in post and post["topic"] is not None:
            post_data += "<div>"
            post_data += "<h3><code class=\"highlight\">" + \
                post["topic"]["content"] + "</code></h3>"
            post_data += "</div>"

        post_data += "<div class=\"content\">"
        post_data += post["content"].replace("\n", "<br/>")
        post_data += "</div><br/>"

        post_data += "<div>"
        pic_path = os.path.join(DIR_PATH, "data/pics/", post["id"])
        for pic in post["pictures"]:
            pic = os.path.join(pic_path, pic["picUrl"].split("?")[0].split("/")[-1])
            post_data += "<div class=\"cropped\"><a href=" + pic + \
                " target=\"_blank\" title=\"open picture\">"
            post_data += "<img src=\"" + pic + "\" alt=\"" + pic + "\" ></a></div>"
        post_data += "</div>"

        if post["type"] == "REPOST" and "content" in post["target"]:
            post_data += "<div><blockquote style=\"color: darkblue\"><div>"
            if "user" in post["target"] and post["target"]["user"] is not None:
                post_data += "<div>"
                post_data += "<h3>" + post["target"]["user"]["screenName"] + "</h3>"
                post_data += "</div>"
            if "topic" in post["target"] and post["target"]["topic"] is not None:
                post_data += "<div>"
                post_data += "<h4>" + post["target"]["topic"]["content"] + "</h4>"
                post_data += "</div>"
            post_data += post["target"]["content"].replace("\n", "<br/>")
            post_data += "<br/><div><br/>"
            post_data += post["target"]["type"] + "<a href=\"https://web.okjike.com/originalPost/" + \
                post["target"]["id"] + "\" target=\"_blank\" title=\"open in Jike\">" + \
                "🔗" + post["target"]["id"]
            post_data += "</a></div><br/>"
            post_data += "</div></blockquote></div><br/>"

        if "linkInfo" in post and post["linkInfo"] is not None:
            post_data += "<div>"
            post_data += "<a href=\"" + post["linkInfo"]["linkUrl"] + \
                "\" target=\"_blank\" title=\"open link\">🔗" + \
                    post["linkInfo"]["title"] + "</a>"
            post_data += "</div><br/>"

        post_data += "<div class=\"like\"><code class=\"highlight\">"
        post_data += "👍 " + str(post["likeCount"])
        post_data += "</code><code class=\"highlight\">"
        post_data += "💬 " + str(post["commentCount"])
        post_data += "</code><code class=\"highlight\">"
        post_data += "🚀 " + str(post["shareCount"])
        post_data += "</code><code class=\"highlight\">"
        post_data += "🔁 " + str(post["repostCount"])
        post_data += "</code></div><br/>"

        post_data += "<div><code class=\"highlight\">"
        post_data += post["type"] + "</code><code><a href=\"https://web.okjike.com/originalPost/" + \
            post["id"] + "\" target=\"_blank\" title=\"open in Jike\">" + \
            "🔗" + post["id"]
        post_data += "</a></code></div><br/>"
        post_data += "</div><hr>"    
        
    data = {
        "curr-time": str(datetime.now(GMT8())),
        "post": post_data,
        "post-count": str(idx+1),
        "post-data-url": post_data_path.replace("\\", "/")
    }
    
    content = template_insert(template_url, data)

    with open(url, "w", encoding="utf8") as f:
        f.write(content)
        # debug(content)


if __name__ == "__main__":
    post_page()
    webbrowser.open_new_tab(url)
    done(url, "opened.")
