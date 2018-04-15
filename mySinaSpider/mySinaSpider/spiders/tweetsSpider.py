# -*- coding: utf-8 -*-
# @Time    : 2018/3/7 18:08
# @Author  : gpf
# @Email   : gpf951101@163.com
# @File    : tweetsSpider.py
# @Software: PyCharm

from scrapy_redis.spiders import RedisSpider
import re
import requests
from scrapy.http import Request
from mySinaSpider.weiboID import weiboID
import datetime
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from mySinaSpider.items import TweetsItem
import time
import random
import logging
from redis import Redis
from mySinaSpider.date_trans import transformDate

logger = logging.getLogger(__name__)

class Spider(RedisSpider):
    name = 'tweetsSpider'
    host = "https://weibo.cn"
    # redis_key = "tweetsSpider:start_urls"

    # 进行redis连接
    r = Redis(host='localhost', port=6379, db=0)
    start_urls = []
    def start_requests(self):
        start_urls = list(set(self.r.lrange("all_user", 0, -1)).difference(set(self.r.lrange("tweet_finish", 0, -1))))
        while len(start_urls) != 0:
            for ID in start_urls:
                url = "{0}/{1}/profile?filter=1&page=1".format(self.host, ID)
                yield Request(url=url, meta={"ID": str(ID)}, callback=self.parse)
            start_urls = list(set(self.r.lrange("all_user", 0, -1)).difference(set(self.r.lrange("tweet_finish", 0, -1))))

    def parse(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweetsItems = TweetsItem()
            id = tweet.xpath('@id').extract_first()  # 微博ID
            content = tweet.xpath('div/span[@class="ctt"]/text()').extract_first()  # 微博内容
            cooridinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标
            like = re.findall(u'\u8d5e\[(\d+)\]', tweet.extract())  # 点赞数
            transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', tweet.extract())  # 转载数
            comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', tweet.extract())  # 评论数
            others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）

            tweetsItems["ID"] = response.meta["ID"]
            tweetsItems["_id"] = response.meta["ID"] + "-" + id
            if content:
                tweetsItems["Content"] = content.strip(u"[\u4f4d\u7f6e]")  # 去掉最后的"[位置]"
            if cooridinates:
                cooridinates = re.findall('center=([\d|.|,]+)', cooridinates)
                if cooridinates:
                    tweetsItems["Co_oridinates"] = cooridinates[0]
            if like:
                tweetsItems["Like"] = int(like[0])
            if transfer:
                tweetsItems["Transfer"] = int(transfer[0])
            if comment:
                tweetsItems["Comment"] = int(comment[0])
            if others:
                others = others.split(u"\u6765\u81ea")
                tweetsItems["PubTime"] = transformDate(others[0])
                if len(others) == 2:
                    tweetsItems["Tools"] = others[1]
            yield tweetsItems
        url_next = selector.xpath(
            u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            logger.info("处理%s的下一页微博" % response.meta['ID'])
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parse)
        else:
            logger.info("%s 的微博处理完毕" % response.meta['ID'])
            self.r.lpush('tweet_finish', response.meta['ID'])
