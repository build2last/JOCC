# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LastfmItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CmtItem(scrapy.Item):
    # 用户某时刻对某首歌发表的评论
    user_name = scrapy.Field()
    time = scrapy.Field()
    mid = scrapy.Field()
    cmt = scrapy.Field()

