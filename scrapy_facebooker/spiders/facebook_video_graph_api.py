import facebook
import scrapy

from scrapy_facebooker.faceblib.graph import get_all_data_from_graph_api
from scrapy_facebooker.items import FacebookVideoGraph


class FacebookVideoGraphSpider(scrapy.Spider):
    name = 'facebook_video_graph'

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
        fb_video_list = get_all_data_from_graph_api(
            self._graph, self.target_username + '/videos')

        for video in fb_video_list:
            video_comments = get_all_data_from_graph_api(
                self._graph, video['id'] + '/comments')
            video_reactions = get_all_data_from_graph_api(
                self._graph, video['id'] + '/reactions')

            fvg = FacebookVideoGraph()
            fvg['fb_id'] = video['id']
            fvg['description'] = video.get('description')
            fvg['updated_time'] = video.get('updated_time')
            fvg['comments'] = video_comments
            fvg['comments_num'] = len(video_comments)
            fvg['reactions'] = video_reactions
            fvg['reactions_num'] = len(video_reactions)
            fvg['fb_video_url'] = (
                'https://web.facebook.com/{username}/videos/{id}'.format(
                    username=self.target_username, id=video['id']
                ))
            yield fvg
