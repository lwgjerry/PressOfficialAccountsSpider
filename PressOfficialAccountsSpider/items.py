# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item
from scrapy import Field

class PressItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    article_url = Field()# 微信文章的URL链接
    press_name = Field()# 出版社名称
    weixin_num = Field()# 微信公众号
    introduction = Field()# 功能介绍
    account_subject = Field()# 账号主体
    title = Field()# 标题
    publish_date = Field()# 发布日期
    read_num = Field()# 阅读数
    like_num = Field()# 点赞数



