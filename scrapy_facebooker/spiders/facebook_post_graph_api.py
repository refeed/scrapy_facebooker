import facebook
import scrapy

from scrapy_facebooker.faceblib.graph import get_all_data_from_graph_api
from scrapy_facebooker.items import FacebookPostGraph


class FacebookPostGraphSpider(scrapy.Spider):
    name = 'facebook_post_graph'

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
        fb_post_list = get_all_data_from_graph_api(
            self._graph, self.target_username + '/posts')

        for post in fb_post_list:
            post_reactions = get_all_data_from_graph_api(
                self._graph, post['id'] + '/reactions')
            post_comments = get_all_data_from_graph_api(
                self._graph, post['id'] + '/comments')

            fpg = FacebookPostGraph()
            fpg['fb_id'] = post['id']
            fpg['url'] = (
                'https://web.facebook.com/{username}/posts/{fbid}'.format(
                    username=self.target_username,
                    fbid=post['id'].split('_')[1]))
            fpg['created_time'] = post.get('created_time')
            fpg['story'] = post.get('story')
            fpg['message'] = post.get('message')
            fpg['comments'] = post_comments
            fpg['comments_num'] = len(post_comments)
            fpg['reactions'] = post_reactions
            fpg['reactions_num'] = len(post_reactions)
            yield fpg
