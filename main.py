import time
import sys
import os
import yaml
import gc
from warning_main import Util

if __name__ == '__main__':
    print("开始监听--")

    # 初始化操作
    ## 创建不存在的数据库
    Util.create_database()
    while True:
    ## 读取rss连接
        config = {}
        with open('config.yaml', 'r') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)["blog_rss_link"]
        # 获取cve_news并发送
        Util.get_huayunan_news()
        Util.get_seebug_news()
        
        # get the rss link and deal with it
        for value in config.values():
            Util.get_blog_from_rss(value)
        # garbage collector
        gc.collect()
        # 设置每一间隔时间
        time.sleep(60 * 20)
