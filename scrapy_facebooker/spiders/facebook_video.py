import datetime
import re
import scrapy

from collections import OrderedDict
from scrapy_facebooker.items import FacebookVideo
from urllib.parse import urlencode, urljoin


class FacebookVideoSpider(scrapy.Spider):
    name = 'facebook_video'
    start_urls = (
        'https://web.facebook.com',
    )
    allowed_domains = ['web.facebook.com']
    top_url = 'https://web.facebook.com'

    def __init__(self, *args, **kwargs):
        self.target_username = kwargs.get('target_username')

        if not self.target_username:
            raise Exception('`target_username` argument must be filled')

    def parse(self, response):
        # Get into target's video page
        return scrapy.Request(
            '{top_url}/pg/{username}/videos/'.format(
                top_url=self.top_url,
                username=self.target_username),
            callback=self._get_facebook_videos_ajax)

    def _get_facebook_videos_ajax(self, response):
        # Get Facebook page's video ajax

        def get_fb_page_id():
            p = re.compile(r'page_id=(\d+)')
            search = re.search(p, str(response.body))
            return search.group(1)

        self.fb_page_id = get_fb_page_id()

        return scrapy.Request(self.create_fb_video_ajax_url(self.fb_page_id,
                                                            '0', '0'),
                              callback=self._parse_fb_video_links)

    def _parse_fb_video_links(self, response):
        # Parse the video links from the ajax response

        html_resp_unicode_decoded = str(
            response.body.decode('unicode_escape')).replace('\\', '')

        def get_next_cursor():
            # Search for next cursor
            cursor_regex = re.compile('cursor\":\"([\w-]+)')
            search_cursor = re.search(cursor_regex, html_resp_unicode_decoded)

            if search_cursor:
                return search_cursor.group(1)
            # If there's no cursor found, that means the current cursor is the
            # last cursor.
            return None

        def get_last_fbid():
            last_fbid_regex = re.compile(r'last_fbid\":(\d+)')
            search_last_fbid = re.search(last_fbid_regex,
                                         html_resp_unicode_decoded)
            return search_last_fbid.group(1)

        # Extract video urls from the fb video ajax response.
        video_url_regex = re.compile(
            r'href=\"(/{username}/videos/\d+)'.format(
                username=self.target_username)
        )
        video_urls = set(
            re.findall(video_url_regex, html_resp_unicode_decoded))

        for video_url in video_urls:
            yield scrapy.Request(
                urljoin(self.top_url, video_url),
                callback=self._parse_video)

        next_cursor = get_next_cursor()
        if next_cursor:
            yield scrapy.Request(self.create_fb_video_ajax_url(self.fb_page_id,
                                                               get_last_fbid(),
                                                               next_cursor),
                                 callback=self._parse_fb_video_links)

    def _parse_video(self, response):
        html_str = str(response.body)

        def get_timestamp():
            timestamp_regex = re.compile(r'data-utime=\"(\d+)')
            timestamp_search = re.search(timestamp_regex, html_str)
            return float(timestamp_search.group(1))

        fvideo = FacebookVideo()
        fvideo['timestamp'] = get_timestamp()
        fvideo['date'] = datetime.datetime.fromtimestamp(
            fvideo['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        fvideo['fb_video_url'] = response.url
        return fvideo

    @staticmethod
    def create_fb_video_ajax_url(page_id, last_fbid, cursor):
        video_ajax_url = urljoin(
            FacebookVideoSpider.top_url,
            '/ajax/pagelet/generic.php/PagesVideoHubVideoContainerPagelet'
        )

        data = ('{"last_fbid":%s,'
                '"page":%s,'
                '"playlist":null,'
                '"cursor":"%s"}' % (last_fbid, page_id, cursor))

        query_str = urlencode(OrderedDict({'data': data,
                                           '__user': 0,
                                           '__a': 1
                                           }))

        return '{ajax_url}/?{query}'.format(ajax_url=video_ajax_url,
                                            query=query_str)
