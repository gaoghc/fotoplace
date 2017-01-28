# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FotoplaceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #pass
    postText = scrapy.Field()
    postId = scrapy.Field()
    bigUrl = scrapy.Field()
    smallUrl = scrapy.Field()
    location = scrapy.Field()
    createTime = scrapy.Field()
    likeNumber = scrapy.Field()
    commentNumber = scrapy.Field()

