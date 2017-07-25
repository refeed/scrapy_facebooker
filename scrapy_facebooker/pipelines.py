# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http import Request


class ScrapyFacebookerPipeline(object):
    def process_item(self, item, spider):
        return item


class FacebookPhotoPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        image_url = item.get('image_url')
        if image_url:
            yield Request(image_url, meta=dict(fb_url=item['url']))

    def get_images(self, response, request, info):
        for path, image, buf, in super(FacebookPhotoPipeline, self).get_images(
                response, request, info):
            new_path = self.change_filepath(response)
            yield new_path, image, buf

    def change_filepath(self, response):
        # Change the path into form:
        # <username>/photos/<album_id>/<photo_cursor>.jpg
        fb_url = response.meta['fb_url']
        new_path_chars = list(fb_url[23:])
        new_path_chars[-1:] = '.jpg'
        return ''.join(new_path_chars)
