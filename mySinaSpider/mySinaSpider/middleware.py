# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from cookies import cookies
from user_agents import agents
import random

class CookiesMiddleware():
    """换cookie"""
    def process_request(self, request, spider):
        cookie = random.choice(cookies)
        request.cookies = cookie

class UserAgentMiddleware():
    """换user_agent"""
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers['User-Agent'] = agent