# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from mySinaSpider.items import FollowsItem, FansItem, TweetsItem, InformationItem
import logging

logger = logging.getLogger(__name__)

class MongoDBPipleline():
    """ 保存信息 """
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['Sina2']
        self.Follows = db['Follows']
        self.Fans = db['Fans']
        self.Tweets = db['Tweets']
        self.Information = db['Information']

    def process_item(self, item, spider):
        """判断类型并处理 加入数据库"""
        if isinstance(item, FollowsItem):
            #关注列表
            try:
                self.Follows.update({'_id': item['_id']}, dict(item), True)
                logger.info("关注信息保存：" + item['_id'])
            except Exception as e:
                print 'Follows Exception'
                print e
        elif isinstance(item, FansItem):
            #关注列表
            try:
                self.Fans.update({'_id': item['_id']}, dict(item), True)
                logger.info("粉丝信息保存：" + item['_id'])
            except Exception as e:
                print 'Fans Exception'
                print e
        elif isinstance(item, TweetsItem):
            #关注列表
            try:
                self.Tweets.update({'_id': item['_id']}, dict(item), True)
                logger.info("微博信息保存：" + item['_id'])
            except Exception as e:
                print 'Tweets Exception'
                print e
        elif isinstance(item, InformationItem):
            try:
                self.Information.update({'_id': item['_id']}, dict(item), True)
                logger.info("个人信息保存：" + item['_id'])
            except Exception as e:
                print 'Information Exception'
                print e
        else:
            print "暂未处理"