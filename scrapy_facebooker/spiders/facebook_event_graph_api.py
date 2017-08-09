import facebook
import scrapy

from scrapy_facebooker.faceblib.graph import get_all_data_from_graph_api
from scrapy_facebooker.items import FacebookEventGraph


class FacebookEventGraphSpider(scrapy.Spider):
    name = 'facebook_event_graph'

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
        # Scrapy `start_requests` wasn't designed for this purpose, it
        # actually designed to fetch html from websites etc, and we
        # here using scrapy for fetching from Facebook Graph API by using
        # `facebook-sdk` library and not `scrapy.Request()`.
        # So we here returning a request to `httpbin.org` to fake the status
        # code, so `parse()` can run normally.
        yield scrapy.Request('http://httpbin.org/status/200',
                             dont_filter=True)

    def parse(self, response):
        fb_event_list = get_all_data_from_graph_api(
            self._graph, self.target_username + '/events')

        for event in fb_event_list:
            event_comments = get_all_data_from_graph_api(
                self._graph, event['id'] + '/comments')

            feg = FacebookEventGraph()
            feg['fb_id'] = event['id']
            feg['url'] = (
                'https://web.facebook.com/events/{eventid}'.format(
                    eventid=event['id']))
            feg['start_time'] = event.get('start_time')
            feg['end_time'] = event.get('end_time')
            feg['description'] = event.get('description')
            feg['comments'] = event_comments
            feg['comments_num'] = len(event_comments)
            feg['place'] = event.get('place')
            feg['name'] = event.get('name')
            yield feg
