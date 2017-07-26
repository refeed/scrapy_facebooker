# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FacebookPost(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    username = scrapy.Field()
    page_title = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    shares_number = scrapy.Field()
    url = scrapy.Field()


class FacebookPhoto(scrapy.Item):
    username = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    timestamp = scrapy.Field()
    image_url = scrapy.Field()


class FacebookEvent(scrapy.Item):
    date = scrapy.Field()
    summary_date = scrapy.Field()
    summary_place = scrapy.Field()
    title = scrapy.Field()
    username = scrapy.Field()
    url = scrapy.Field()


class FacebookVideo(scrapy.Item):
    timestamp = scrapy.Field()
    date = scrapy.Field()
    fb_video_url = scrapy.Field()
