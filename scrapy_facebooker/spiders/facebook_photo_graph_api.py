import facebook
import scrapy

from bs4 import BeautifulSoup
from scrapy_facebooker.faceblib.graph import get_all_data_from_graph_api
from scrapy_facebooker.faceblib.url import (
    create_facebook_photo_url_from_photo_id
)
from scrapy_facebooker.items import FacebookPhotoGraph


class FacebookPhotoGraphSpider(scrapy.Spider):
    name = 'facebook_photo_graph'

    def __init__(self, *args, **kwargs):
        self.target_username = kwargs.get('target_username')
        self.access_token = kwargs.get('access_token')

        if not self.target_username:
            raise Exception('`target_username` argument must be filled')
        if not self.access_token:
            raise Exception('`access_token` argument must be filled')

        self._graph = facebook.GraphAPI(access_token=self.access_token,
                                        version='2.7')

    def start_requests(self):
        photo_data_list = self.get_fb_photo_list()

        for data in photo_data_list:
            yield scrapy.Request(
                create_facebook_photo_url_from_photo_id(data['id'],
                                                        self.target_username),
                meta=data,
                dont_filter=True)

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        photo_reactions = get_all_data_from_graph_api(
            self._graph, response.meta['id'] + '/reactions')
        photo_comments = get_all_data_from_graph_api(
            self._graph, response.meta['id'] + '/comments')

        fphotograph = FacebookPhotoGraph()
        fphotograph['fb_id'] = response.meta['id']
        fphotograph['created_time'] = response.meta.get('created_time')
        fphotograph['url'] = response.url
        fphotograph['name'] = response.meta.get('name')
        fphotograph['comments'] = photo_comments
        fphotograph['comments_num'] = len(photo_comments)
        fphotograph['reactions'] = photo_reactions
        fphotograph['reactions_num'] = len(photo_reactions)
        fphotograph['image_url'] = soup.find(
            'meta', property='og:image')['content']
        return fphotograph

    def get_fb_photo_list(self):
        photo_paths = ['/photos',
                       '/photos/tagged',
                       '/photos/profile',
                       '/photos/uploaded']

        photo_data_list = []
        for photo_path in photo_paths:
            photo_data_list.extend(get_all_data_from_graph_api(
                self._graph, self.target_username + photo_path
            ))
        return photo_data_list
