'''
这是seebug的漏洞库
'''
import feedparser
import re
import sqlite3
from warning_main import Util

def save_none_CVE(title):
    con = sqlite3.connect('cve_monitor.db')
    cur = con.cursor()
    cur.execute("INSERT INTO cve_monitor (vuln_name, cve_name, cve_url, pushed_at) VALUES ('{}', '{}', '{}', '{}') \
                            ".format("0", title, "0", "0"))
    con.commit()
    con.close()

def get_data():
    '''
    获取数据
    '''
    rent_list = []     # 漏洞名
    cve_list = []      # CVE号
    warning_list = []  # 危险级别
    time_list = []     # 发布时间
    url_list = []      # 详细url
    detail_list = []   # 细节描述

    data_tmp = []
    NewsFeed = feedparser.parse("https://www.seebug.org/rss/new/")
    entry = NewsFeed.entries
    try:
        for i in range(len(entry)):
            rent_list.append(entry[i]['title'])
            # 保证没有CVE编号也能收到消息
            if 'CVE' not in entry[i]['title']:
                cve_list.append("CVE-1111-1111")
                warning_list.append(" ")
                url_list.append(entry[i]['link'])
                detail_list.append(entry[i]['summary'])
                time_list.append(entry[i]['updated_date'])
                
                Verify = Util.query_cve_info_database(entry[i]['title'])
                if Verify == 0:
                    Util.sendAPI("seebug出现没有CVE的标题\r\n{}".format(entry[i]['title']))
                    Util.logger.error("seebug出现没有CVE的标题\r\n{}".format(entry[i]['title']))
                    save_none_CVE(entry[i]['title'])
                continue
            cve = re.findall(r'(CVE\-\d+\-\d+)', entry[i]['title'])[0].upper()
            cve_list.append(cve)
            warning_list.append(" ")
            url_list.append(entry[i]['link'])
            detail_list.append(entry[i]['summary'])
            time_list.append(entry[i]['updated_date'])
        for i in range(len(rent_list)):
            data_tmp.append({"vuln_name": rent_list[i], "cve_name": cve_list[i], "warning": warning_list[i],
                                "pushed_at": time_list[i], "cve_url": url_list[i], "detail": detail_list[i]})
    except Exception as e:
        Util.sendAPI("seebug错误warning\r\n抓取信息出现错误{}".format(e))
        Util.logger.error("seebug错误warning\r\n抓取信息出现错误{}".format(e))
        pass
    return data_tmp