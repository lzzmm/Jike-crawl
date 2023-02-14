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
#       function to call

template_url = os.path.join(DIR_PATH, "data/pages/template.html")
url = os.path.join(DIR_PATH, "data/pages/posts.html")

content = ""

with open(template_url, "r", encoding="utf8") as f:
    content = f.read()
    # debug(content)

posts = read_multi_json_file(os.path.join(DIR_PATH, "data/posts.json"))
# debug(posts[:3])

data = "Generated at " + str(datetime.now(GMT8())) + "<br/><hr>"

# TODO: some way to filter posts like topic / create time
start_index = None
end_index = None

for post in posts[start_index:end_index]:
    data += "<div class=\"post\"><h2>"
    data += str(datetime.strptime(post['createdAt'], "%Y-%m-%dT%X.%fZ").replace(
        tzinfo=UTC()).astimezone(GMT8()).__format__("%Y-%m-%d %X (%Z)"))
    data += "</h2>"

    if "topic" in post and post["topic"] is not None:
        data += "<div>"
        data += "<h3>" + post["topic"]["content"] + "</h3>"
        data += "</div>"

    data += "<div>"
    data += post["content"].replace("\n", "<br/>")
    data += "</div><br/>"

    data += "<div>"
    pic_path = os.path.join(DIR_PATH, "data/pics/", post["id"])
    for pic in post["pictures"]:
        pic = os.path.join(pic_path, pic["picUrl"].split("?")[0].split("/")[-1])
        data += "<a href=" + pic + "><div class=\"cropped\">"
        data += "<img src=\"" + pic + "\" alt=\"" + pic + "\" ></div></a>"
    data += "</div>"
    
    if post["type"] == "REPOST" and "content" in post["target"]:
        data += "<div><blockquote style=\"color: darkblue\"><div>"
        if "user" in post["target"] and post["target"]["user"] is not None:
            data += "<div>"
            data += "<h3>" + post["target"]["user"]["screenName"] + "</h3>"
            data += "</div>"
        if "topic" in post["target"] and post["target"]["topic"] is not None:
            data += "<div>"
            data += "<h4>" + post["target"]["topic"]["content"] + "</h4>"
            data += "</div>"
        data += post["target"]["content"].replace("\n", "<br/>")
        data += "<br/><div><br/>"
        data += post["target"]["type"] + " - <a href=\"https://web.okjike.com/originalPost/" + \
            post["target"]["id"] + "\">" + post["target"]["id"]
        data += "</a></div><br/>"
        data += "</div></blockquote></div><br/>"
        
    if "linkInfo" in post and post["linkInfo"] is not None:
        data += "<div>"
        data += "<a href=\"" + post["linkInfo"]["linkUrl"] + "\">" + post["linkInfo"]["title"] + "</a>"
        data += "</div><br/>"


    data += "<div><div>"
    data += "like: " + str(post["likeCount"])
    data += " " # "</div><div>"
    data += "comment: " + str(post["commentCount"])
    data += " " # "</div><div>"
    data += "share: " + str(post["shareCount"])
    data += " " # "</div><div>"
    data += "repost: " + str(post["repostCount"])
    data += "</div></div><br/>"

    data += "<div>"
    data += post["type"] + " - <a href=\"https://web.okjike.com/originalPost/" + \
        post["id"] + "\">" + post["id"]
    data += "</a></div><br/>"
    data += "</div><hr>"

contents = content.split("{%data%}")

content = contents[0] + data + contents[1]

with open(url, "w", encoding="utf8") as f:
    f.write(content)
    # debug(content)

webbrowser.open_new_tab(url)
done(url, "opened.")
