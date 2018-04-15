# -*- coding: utf-8 -*-
# @Time    : 2018/3/8 16:46
# @Author  : gpf
# @Email   : gpf951101@163.com
# @File    : FollowsSpider.py
# @Software: PyCharm

from scrapy_redis.spiders import RedisSpider
import re
import requests
from scrapy.http import Request
from mySinaSpider.weiboID import weiboID
import datetime
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from mySinaSpider.items import FollowsItem
import time
import random
import logging
from redis import Redis

logger = logging.getLogger(__name__)

class Spider(RedisSpider):
    name = 'followsSpider'
    host = "https://weibo.cn"
    #redis_key = "followsSpider:start_urls"
    start_urls = []

    r = Redis(host='localhost', port=6379, db=0)
    start_urls = []

    def start_requests(self):
        start_urls = list(set(self.r.lrange("all_user", 0, -1)).difference(set(self.r.lrange("follow_finish", 0, -1))))
        while len(start_urls) != 0:
            for ID in start_urls:
                follows = []
                followsItems = FollowsItem()
                followsItems["_id"] = str(ID)
                followsItems["follows"] = follows
                url = "{0}/{1}/follow".format(self.host, ID)
                yield Request(url=url, meta={"item": followsItems, "result": follows}, callback=self.parse)
            start_urls = list(set(self.r.lrange("all_user", 0, -1)).difference(set(self.r.lrange("follow_finish", 0, -1))))


    def parse(self, response):
        """ 抓取关注或粉丝 """
        items = response.meta["item"]
        selector = Selector(response)
        text2 = selector.xpath(
            u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()
        for elem in text2:
            elem = re.findall('uid=(\d+)', elem)
            if elem:
                # 将关注人加入全部用户
                response.meta["result"].append(elem[0])
        url_next = selector.xpath(
            u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"item": items, "result": response.meta["result"]},
                          callback=self.parse)
        else:  # 如果没有下一页即获取完毕
            logger.info("%s 的关注列表以完毕" % items['_id'])
            # if len(self.r.lrange("all_user", 0, -1)) <= 600:
            #     for u in response.meta['result']:
            #         self.r.lpush('all_user', u)
            #     logger.info("%s 关注用户加入到 all_user成功..." % items['_id'])
            self.r.lpush('follow_finish', items['_id'])
            yield items