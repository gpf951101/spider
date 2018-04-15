# -*- coding: utf-8 -*-
# @Time    : 2018/3/8 16:48
# @Author  : gpf
# @Email   : gpf951101@163.com
# @File    : InfoSpider.py
# @Software: PyCharm

from scrapy_redis.spiders import RedisSpider
import re
import requests
from scrapy.http import Request
from mySinaSpider.weiboID import weiboID
import datetime
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from mySinaSpider.items import InformationItem
import time
import random
import logging
from redis import Redis

logger = logging.getLogger(__name__)

class Spider(RedisSpider):
    name = 'infoSpider'
    host = "https://weibo.cn"
    #redis_key = "infoSpider:start_urls"

    r = Redis(host='localhost', port=6379, db=0)
    start_urls = []

    def start_requests(self):
        start_urls = list(set(self.r.lrange("all_user", 0, -1)).difference(set(self.r.lrange("info_finish", 0, -1))))
        while len(start_urls) != 0:
            for ID in start_urls:
                url = "{0}/attgroup/opening?uid={1}".format(self.host, ID)
                yield Request(url=url, meta={"ID": str(ID)}, callback=self.parse0)
            start_urls = list(set(self.r.lrange("all_user", 0, -1)).difference(set(self.r.lrange("info_finish", 0, -1))))

    def parse0(self, response):
        """ 抓取个人信息1 """
        informationItems = InformationItem()
        selector = Selector(response)
        text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
        if text0:
            num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
            num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
            num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
            if num_tweets:
                informationItems["Num_Tweets"] = int(num_tweets[0])
            if num_follows:
                informationItems["Num_Follows"] = int(num_follows[0])
            if num_fans:
                informationItems["Num_Fans"] = int(num_fans[0])
            informationItems["_id"] = response.meta["ID"]
            url_information1 = "{0}/{1}/info".format(self.host, response.meta["ID"])
            yield Request(url=url_information1, meta={"item": informationItems}, callback=self.parse1)

    def parse1(self, response):
        """ 抓取个人信息2 """
        informationItems = response.meta["item"]
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)  # 昵称
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
        place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
        signature = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1)  # 个性签名
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  # 生日
        sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', text1)  # 性取向
        marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)  # 婚姻状况
        url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  # 首页链接

        if nickname:
            informationItems["NickName"] = nickname[0]
        if gender:
            informationItems["Gender"] = gender[0]
        if place:
            place = place[0].split(" ")
            informationItems["Province"] = place[0]
            if len(place) > 1:
                informationItems["City"] = place[1]
        if signature:
            informationItems["Signature"] = signature[0]
        if birthday:
            try:
                birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                informationItems["Birthday"] = birthday - datetime.timedelta(hours=8)
            except Exception:
                pass
        if sexorientation:
            if sexorientation[0] == gender[0]:
                informationItems["Sex_Orientation"] = "gay"
            else:
                informationItems["Sex_Orientation"] = "Heterosexual"
        if marriage:
            informationItems["Marriage"] = marriage[0]
        if url:
            informationItems["URL"] = url[0]
        logger.info("%s 的个人信息处理完毕" % informationItems['_id'])
        self.r.lpush('info_finish', informationItems['_id'])
        yield informationItems