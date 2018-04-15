# -*- coding: utf-8 -*-
# @Time    : 2018/3/7 17:15
# @Author  : gpf
# @Email   : gpf951101@163.com
# @File    : cookies.py
# @Software: PyCharm

import sys
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
import time
from lxml import etree
import random
from mySinaSpider.login import getType, draw
from redis import Redis

reload(sys) #重新加载sys 进而设置默认的编码
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)

myWeiBo = [
    {'no': '18716002183', 'psw': '201406'},
    #{'no': '18810392213', 'psw': '201406'}
]

def getCookies(weibo):
    """获取cookies"""
    logger.info("BEGIN GET COOKIES")
    cookies = []

    for elem in weibo:
        account = elem['no']
        password = elem['psw']
        cookie = getCookie(account, password)
        if cookie != None:
            cookies.append(cookie)

    return cookies

def getCookie(account, password):
    """获取单个cookie,模拟登陆"""
    logger.info("get cookie")
    try:
        chrome_options = Options()
        chrome_options.add_argument('--dns-prefetch-disable')
        display = Display(visible=0, size=(800, 800))
        display.start()
        logger.info("模拟器启动成功")
        browser = webdriver.Chrome(chrome_options=chrome_options)
        logger.info("浏览器获取成功")
        browser.get("https://weibo.cn/login")
        logger.info("访问登录界面成功")
        time.sleep(5)
        failure = 0
        while "微博" in browser.title and failure < 5:
            failure += 1
            logger.info("第 %s 次尝试进行登陆"%(failure))
            username = browser.find_element_by_id("loginName")
            username.clear()
            username.send_keys(account)
            psd = browser.find_element_by_xpath("//input[@type='password']")
            psd.clear()
            psd.send_keys(password)
            commit = browser.find_element_by_id("loginAction")
            commit.click()
            logger.info("用户名、密码填写成功")
            browser.save_screenshot("aa.png")
            cookie = {}

            # if '我的首页' not in browser.title:
            #     logger.info("开始处理验证码")
            #     try:
            #         ttype = getType(browser)
            #         logger.info("验证码内容：%s" % ttype)
            #         draw(browser, ttype)
            #         time.sleep(random.randint(10, 20))
            #         logger.info("验证码处理完毕")
            #     except Exception, e:
            #         logger.error("验证码处理错误：\n %s " % e)

            if '我的首页' not in browser.title:
                time.sleep(random.randint(5, 10))
            if '未激活微博' in browser.page_source:
                logger.error("账号未开通")
                return {}

            if "我的首页" in browser.title:
                logger.warning("登陆成功!")
                for elem in browser.get_cookies():
                    cookie[elem['name']] = elem['value']
                logger.warning("Get Cookie Success!(Account: %s)" % account)
            return cookie

    except Exception, e:
        logger.warning("Failed %s!" % account)
        logger.error(e)
        return None
    finally:
        try:
            browser.close()
            display.stop()
        except Exception, e:
            logger.error("模拟器关闭失败")

cookies = getCookies(myWeiBo)
logger.warning('GetCookies Finish(Num: %d)' % len(cookies))
r = Redis(host='localhost', port=6379, db=0)
r.lpush("all_user", "5861859392")
r.lpush("all_user", "2313896275")
logger.info("用户初始化成功。。。")