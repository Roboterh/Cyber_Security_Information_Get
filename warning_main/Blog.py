'''
This is a module to get articles from rss
'''
import feedparser
import requests
from io import BytesIO
from warning_main import Util

def get_data(rss):
    '''
    get data from page
    '''
    title_list = []
    link_list = []
    summary_list = []
    pushed_at_list = []

    data_tmp = []
    
    BlogsFeed = feedparser.parse(rss)
    entry = BlogsFeed.entries
    try:
        for i in range(len(entry)):
            title_list.append(entry[i]['title'])
            link_list.append(entry[i]['link'])
            try:
                summary_list.append(entry[i]['summary'])
            except KeyError:
                summary_list.append("None")
            try:
                pushed_at_list.append(entry[i]['published'])
            except KeyError:
                try:
                    pushed_at_list.append(entry[i]['updated'])
                except KeyError:
                    pushed_at_list.append("None")
        for i in range(len(title_list)):
            data_tmp.append({"title": title_list[i], "link": link_list[i], "summary": summary_list[i], "pushed_at": pushed_at_list[i]})
    except Exception as e:
        Util.sendAPI("Blog.py错误warning\r\n抓取信息出现错误{}".format(e))
        Util.logger.error("Blog.py错误warning\r\n抓取信息出现错误{}".format(e))
        pass
    return data_tmp
