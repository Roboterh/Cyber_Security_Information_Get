"""
一个工具类
"""
import re
import dingtalkchatbot as cb
from warning_main import logging_config
from warning_main import huayunan
from warning_main import seebug
from warning_main import Blog
import requests
import yaml
import json
import sqlite3

logger = logging_config.Config().get_config()

def sendAPI(text):
    url_tmp = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=xx&corpsecret=xx"
    res = requests.get(url_tmp)
    # print(res.json())
    access_token = res.json()['access_token']
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(access_token)
    data = {
        "toparty" : "1",
        "msgtype" : "text",
        "agentid" : 1000002,
        "text" : {
            "content" : ""
        },
        "safe":0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    data['text']['content'] = text
    requests.post(url, data=json.dumps(data))

def loadConfig():
    '''
    获取Server酱等的配置
    '''
    # filename = os.path.dirname(os.path.realpath(__file__)) + "\\config.yaml"
    with open('config.yaml', 'r') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
        if int(config['all_config']['dingding'][0]['enable']) == 1:
            dingding_webhook = config['all_config']['dingding'][1]['webhook']
            dingding_secretKey = config['all_config']['dingding'][2]['secretKey']
            app_name = config['all_config']['dingding'][3]['app_name']
            return app_name,dingding_webhook,dingding_secretKey
        elif int(config['all_config']['feishu'][0]['enable']) == 1:
            feishu_webhook = config['all_config']['feishu'][1]['webhook']
            app_name = config['all_config']['feishu'][2]['app_name']
            return app_name,feishu_webhook,feishu_webhook
        elif int(config['all_config']['server'][0]['enable']) == 1:
            server_sckey = config['all_config']['server'][1]['sckey']
            app_name = config['all_config']['server'][2]['app_name']
            return app_name,server_sckey
        elif int(config['all_config']['pushplus'][0]['enable']) == 1:
            pushplus_token = config['all_config']['pushplus'][1]['token']
            app_name = config['all_config']['pushplus'][2]['app_name']
            return app_name,pushplus_token            
        elif int(config['all_config']['tgbot'][0]['enable']) ==1 :
            tgbot_token = config['all_config']['tgbot'][1]['token']
            tgbot_group_id = config['all_config']['tgbot'][2]['group_id']
            app_name = config['all_config']['tgbot'][3]['app_name']
            return app_name,tgbot_token,tgbot_group_id
        elif int(config['all_config']['tgbot'][0]['enable']) == 0 and int(config['all_config']['feishu'][0]['enable']) == 0 and int(config['all_config']['server'][0]['enable']) == 0 and int(config['all_config']['pushplus'][0]['enable']) == 0 and int(config['all_config']['dingding'][0]['enable']) == 0:
            info = "[-] 配置文件有误，五个社交软件的enable不能为0"
            print(info)
            logger.error(info)

def create_database():
    '''
    初始化创建数据库 cve_monitor.db
    '''
    conn = sqlite3.connect('cve_monitor.db')
    cur = conn.cursor()
    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS cve_monitor
                    (vuln_name varchar(255), 
                    cve_name varchar(255),
                    cve_url varchar(255),
                    pushed_at varchar(255));''')
        cur.execute('''CREATE TABLE IF NOT EXISTS blog_monitor
                    (title varchar(255),
                    link varchar(255),
                    summary varchar(255),
                    pushed_at varchar(255));''')
        print("成功创建cve_monitor表, blog_monitor表")
        logger.info("成功创建cve_monitor表, blog_monitor表")
    except Exception as e:
        print("创建表错误，错误为{}".format(e))
        logger.debug("创建表错误，错误为{}".format(e))
    conn.commit() # 将数据存入硬盘中
    conn.close() # 关闭资源
    if loadConfig()[0] == 'dingding':
        dingding("test", "连接成功", loadConfig()[1], loadConfig()[2])
    elif loadConfig()[0] == "server":
        # server("test", "连接成功", loadConfig()[1])
        sendAPI("test\r\n连接成功")
    elif loadConfig()[0] == "pushplus":
        pushplus("test", "连接成功", loadConfig()[1])        
    elif loadConfig()[0] == "tgbot":
        tgbot("test", "连接成功", loadConfig()[1], loadConfig()[2])

def dingding(text, msg,webhook,secretKey):
    '''
    使用钉钉推送消息
    '''
    ding = cb.DingtalkChatbot(webhook, secret=secretKey)
    ding.send_text(msg='{}\r\n{}'.format(text, msg), is_at_all=False)

def feishu(text,msg,webhook):
    '''
    使用飞书推送消息
    '''
    ding = cb.DingtalkChatbot(webhook)
    ding.send_text(msg='{}\r\n{}'.format(text, msg), is_at_all=False)

def server(text, msg,sckey):
    '''
    使用Server酱联动企业微信推送消息
    http://sc.ftqq.com/?c=code
    '''
    try:
        uri = 'https://sctapi.ftqq.com/{}.send?text={}&desp={}'.format(sckey,text, msg)# 将 xxxx 换成自己的server SCKEY
        requests.get(uri, timeout=10)
    except Exception as e:
        pass

def pushplus(text, msg,token):
    '''
    使用pushplus
    https://www.pushplus.plus/push1.html
    '''
    try:
        uri = 'https://www.pushplus.plus/send?token={}&title={}&content={}'.format(token,text, msg)# 将 xxxx 换成自己的pushplus的 token
        requests.get(uri, timeout=10)
    except Exception as e:
        pass        

def tgbot(text, msg,token,group_id):

    '''
    使用Telegram Bot推送
    '''
    import telegram
    try:
        bot = telegram.Bot(token='{}'.format(token))# Your Telegram Bot Token
        bot.send_message(chat_id=group_id, text='{}\r\n{}'.format(text, msg))
    except Exception as e:
        pass

def sendNews(data):
    '''
    向社交平台发送消息
    '''
    try:
        for i in range(len(data)):
            try:
                text = data[i]['vuln_name'] # 发送消息的标题
                # 消息的内容
                body = text + "\r\n" + "CVE编号: " + data[i]['cve_name'] + "\r\n" + "威胁: " + data[i]['warning'] + "\r\n" \
                    "地址: " + data[i]['cve_url'] + "\r\n" + "发布时间: " + data[i]['pushed_at'] + "\r\n" + "漏洞描述: " + data[i]['detail']
                if loadConfig()[0] == "dingding":
                    dingding(text, body, loadConfig()[1], loadConfig()[2])
                    print("钉钉 发送 CVE 成功")
                    logger.info("钉钉 发送 CVE 成功")
                elif loadConfig()[0] == "feishu":
                    feishu(text, body, loadConfig()[1])
                    print("飞书 发送 CVE 成功")
                    logger.info("飞书 发送 CVE 成功")
                elif loadConfig()[0] == "server":
                    # server(text, body, loadConfig()[1])
                    sendAPI(body)
                    print("WeChat 发送 CVE 成功")
                    logger.info("WeChat 发送 CVE 成功")
                elif loadConfig()[0] == "pushplus":
                    pushplus(text, body, loadConfig()[1])
                    print("pushplus 发送 CVE 成功")
                    logger.info("pushplus 发送 CVE 成功")                    
                elif loadConfig()[0] == "tgbot":
                    tgbot(text, body, loadConfig()[1], loadConfig()[2])
                    print("tgbot 发送 CVE 成功")
                    logger.info("tgbot 发送 CVE 成功")
            except Exception as e:
                pass
    except Exception as e:
        sendAPI("发送消息发生错误warning\r\n错误为{}".format(e))
        print("sendNews发生了错误, 错误为：{}".format(e))
        logger.error("sendNews发生了错误, 错误为：{}".format(e))

def sendArticles(data):
    '''
    send new articles to social platforms
    '''
    try:
        for i in range(len(data)):
            try:
                text = data[i]['title'] # 发送消息的标题
                # 消息的内容
                body = text + "\r\n" + "article_title: " + data[i]['title'] + "\r\n" + "summary: " + data[i]['summary'] + "\r\n" \
                    "link: " + data[i]['link'] + "\r\n" + "pushed_time: " + data[i]['pushed_at']
                if loadConfig()[0] == "dingding":
                    dingding(text, body, loadConfig()[1], loadConfig()[2])
                    print("钉钉 发送 blog 成功")
                    logger.info("钉钉 发送 blog 成功")
                elif loadConfig()[0] == "feishu":
                    feishu(text, body, loadConfig()[1])
                    print("飞书 发送 blog 成功")
                    logger.info("飞书 发送 blog 成功")
                elif loadConfig()[0] == "server":
                    # server(text, body, loadConfig()[1])
                    sendAPI(body)
                    print("WeChat 发送 blog 成功")
                    logger.info("WeChat 发送 blog 成功")
                elif loadConfig()[0] == "pushplus":
                    pushplus(text, body, loadConfig()[1])
                    print("pushplus 发送 blog 成功")   
                    logger.info("pushplus 发送 blog 成功")                 
                elif loadConfig()[0] == "tgbot":
                    tgbot(text, body, loadConfig()[1], loadConfig()[2])
                    print("tgbot 发送 blog 成功")
                    logger.info("tgbot 发送 blog 成功")
            except Exception as e:
                pass
    except Exception as e:
        sendAPI("发送消息发生错误warning\r\n错误为{}".format(e))
        print("sendArticles发生了错误, 错误为：{}".format(e))
        logger.error("sendArticles发生了错误, 错误为：{}".format(e))

def save_to_database(data):
    '''
    将关键信息加入数据库
    '''
    conn = sqlite3.connect('cve_monitor.db')
    cur = conn.cursor()
    for i in range(len(data)):
        try:
            cve_name = re.findall('(CVE\-\d+\-\d+)', data[i]['cve_name'])[0].upper()
            cur.execute("INSERT INTO cve_monitor (vuln_name, cve_name, cve_url, pushed_at) VALUES ('{}', '{}', '{}', '{}') \
                            ".format(data[i]['vuln_name'], cve_name, data[i]['cve_url'], data[i]['pushed_at']))
            print("插入{}数据成功".format(cve_name))
            logger.info("插入{}数据成功".format(cve_name))
        except Exception as e:
            sendAPI("插入数据发生错误warning\r\n失败报错{}".format(e))
            print("save_to_database失败, 错误为：{}".format(e))
            logger.error("save_to_database失败, 错误为：{}".format(e))
            pass
    conn.commit() # 存入硬盘
    conn.close()

def save_to_database_blog(data):
    '''
    save summary to table blog_monitor
    '''
    conn = sqlite3.connect('cve_monitor.db')
    cur = conn.cursor()
    for i in range(len(data)):
        try:
            blog_title = data[i]['title']
            cur.execute("INSERT INTO blog_monitor (title, link, summary, pushed_at) VALUES ('{}', '{}', '{}', '{}') \
                            ".format(data[i]['title'], data[i]['link'], data[i]['summary'], data[i]['pushed_at']))
            print("插入{}数据成功".format(blog_title))
            logger.info("插入{}数据成功".format(blog_title))
        except Exception as e:
            cur.execute("INSERT INTO blog_monitor (title, link, summary, pushed_at) VALUES ('{}', '{}', '{}', '{}') \
                            ".format(data[i]['title'], data[i]['link'], "None", data[i]['pushed_at']))
            sendAPI("插入数据发生错误warning\r\n失败报错{}".format(e))
            print("save_to_database_blog失败, 错误为：{}".format(e))
            logger.error("save_to_database_blog失败, 错误为：{}".format(e))
            pass
    conn.commit() # 存入硬盘
    conn.close()

def query_cve_info_database(cve_name):
    '''
    查看数据库中是否有cve_name
    '''
    con = sqlite3.connect('cve_monitor.db')
    cur = con.cursor()
    content = cur.execute("SELECT cve_name FROM cve_monitor WHERE cve_name = '{}';".format(cve_name))
    return len(list(content))

def query_blog_info_database(blog_title):
    '''
    see if there is blog_title in database
    '''
    con = sqlite3.connect('cve_monitor.db')
    cur = con.cursor()
    content = cur.execute("SELECT title FROM blog_monitor WHERE title = '{}';".format(blog_title))
    return len(list(content))

def get_new_cve_name(data):
    '''
    获取数据库不存在的cve
    '''
    new_cve = []
    for i in range(len(data)):
        try:
            new_cve_name = re.findall('(CVE\-\d+\-\d+)', data[i]['cve_name'])[0].upper()
            Verify = query_cve_info_database(new_cve_name)
            if Verify == 0:
                print("[+] 数据库里不存在{}".format(new_cve_name.upper()))
                logger.info("[+] 数据库里不存在{}".format(new_cve_name.upper()))
                new_cve.append(data[i])
            else:
                print("[-] 数据库里存在{}".format(new_cve_name.upper()))
                logger.info("[-] 数据库里存在{}".format(new_cve_name.upper()))
        except Exception as e:
            print("get_new_cve_name出问题, 问题是：{}".format(e))
            logger.error("get_new_cve_name出问题, 问题是：{}".format(e))
            pass
    return new_cve

def get_new_blog_title(data):
    '''
    get the blog'title that is not in database
    '''
    new_blog = []
    for i in range(len(data)):
        try:
            new_blog_title = data[i]['title']
            Verify = query_blog_info_database(new_blog_title)
            if Verify == 0:
                print("[+] 数据库里不存在{}".format(new_blog_title))
                logger.info("[+] 数据库里不存在{}".format(new_blog_title))
                new_blog.append(data[i])
            else:
                print("[-] 数据库里存在{}".format(new_blog_title))
                logger.info("[-] 数据库里存在{}".format(new_blog_title))
        except Exception as e:
            print("get_new_cve_name出问题, 问题是：{}".format(e))
            logger.error("get_new_cve_name出问题, 问题是：{}".format(e))
            pass
    return new_blog

def get_huayunan_news():
    '''
    获取华云安的安全资讯
    '''
    news = huayunan.get_data()

    new_vuln = get_new_cve_name(news)
    sendNews(new_vuln)
    # sendAPI(new_vuln)
    save_to_database(new_vuln)

def get_seebug_news():
    '''
    获取seebug的资讯
    '''
    news = seebug.get_data()

    new_vuln = get_new_cve_name(news)
    sendNews(new_vuln)
    # sendAPI(new_vuln)
    save_to_database(new_vuln)

def get_blog_from_rss(rss):
    '''
    get the latest articles from rss
    '''
    articles = Blog.get_data(rss)

    new_articles = get_new_blog_title(articles)
    sendArticles(new_articles)
    save_to_database_blog(new_articles)
