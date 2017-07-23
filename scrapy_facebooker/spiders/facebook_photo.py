import datetime
import re
import scrapy

from bs4 import BeautifulSoup
from collections import OrderedDict
from scrapy_facebooker.items import FacebookPhoto
from urllib.parse import urlencode


class FacebookPhotoSpider(scrapy.Spider):
    name = 'facebook_photo'
    start_urls = (
        'http://m.facebook.com/',
    )
    allowed_domains = ['m.facebook.com']
    top_url = 'http://m.facebook.com'

    def __init__(self, *args, **kwargs):
        self.target_username = kwargs.get('target_username')

        if not self.target_username:
            raise Exception('`target_username` argument must be filled')

    def parse(self, response):
        # Get into target's Facebook albums page.
        return scrapy.Request(
            '{top_url}/{username}/photos/'.format(
                top_url=self.top_url,
                username=self.target_username),
            callback=self._get_facebook_photos_ajax)

    def _get_facebook_photos_ajax(self, response):
        # Get Facebook page's photo ajax

        def get_first_cursor():
            soup = BeautifulSoup(response.body, 'html.parser')
            # Search for the first photo url in the page, cursor
            # is placed in the photo url.
            first_photo_element = soup.find('div', class_='_5v64').find('a')
            cursor_regex = re.compile(r'/.+/photos/a\.[\d\.]+/(\d+)/')
            cursor = re.search(cursor_regex, first_photo_element['href']
                               ).group(1)
            return cursor

        def get_fb_page_id():
            p = re.compile(r'page_id&quot;:(\d+)')
            search = re.search(p, str(response.body))
            return search.group(1)

        self.fb_page_id = get_fb_page_id()

        return scrapy.Request(self.create_fb_photo_ajax_url(self.fb_page_id,
                                                            get_first_cursor()
                                                            ),
                              callback=self._parse_fb_photo_links)

    def _parse_fb_photo_links(self, response):
        html_resp_unicode_decoded = str(
            response.body.decode('unicode_escape')).replace('\\', '')

        def get_next_cursor():
            # Search for next cursor
            cursor_regex = re.compile('cursor=(\d+)')
            search_cursor = re.search(cursor_regex, html_resp_unicode_decoded)

            if search_cursor:
                return search_cursor.group(1)
            # If there's no cursor found, that means the current cursor is the
            # last cursor.
            return None

        # Extract photo urls from the fb photo ajax response.
        photo_url_regex = re.compile(
            r'href=\"(/{username}/photos/a.[\d\./]+)'.format(
                username=self.target_username))
        photo_urls = set(
            re.findall(photo_url_regex, html_resp_unicode_decoded))

        for photo_url in photo_urls:
            yield scrapy.Request('{top_url}/{photo_url}'.format(
                top_url=self.top_url,
                photo_url=photo_url),
                callback=self._parse_photo)

        # Check if there's a next cursor attached in the fb photo ajax
        # response.
        next_cursor = get_next_cursor()
        if next_cursor:
            yield scrapy.Request(self.create_fb_photo_ajax_url(self.fb_page_id,
                                                               next_cursor),
                                 callback=self._parse_fb_photo_links)

    def _parse_photo(self, response):
        html_str = str(response.body)
        soup = BeautifulSoup(html_str, 'html.parser')

        def get_timestamp():
            timestamp_regex = re.compile(r'time&quot;:(\d+)')
            timestamp = re.search(timestamp_regex, html_str).group(1)
            return float(timestamp)

        fphoto = FacebookPhoto()
        fphoto['username'] = self.target_username
        fphoto['url'] = response.url
        fphoto['image_url'] = soup.find('meta', property='og:image')['content']
        fphoto['timestamp'] = get_timestamp()
        fphoto['date'] = datetime.datetime.fromtimestamp(
            fphoto['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

        return fphoto

    @staticmethod
    def create_fb_photo_ajax_url(fb_page_id, cursor):
        ajax_photo_url = 'https://m.facebook.com/photos/pandora'

        album_token_query = (
            'pb.{page_id}.-2207520000.1500733574.'.format(page_id=fb_page_id))

        query_str = urlencode(OrderedDict(album_token=album_token_query,
                                          cursor=cursor,
                                          impression_source=54))
        return '{0}/?{1}'.format(ajax_photo_url, query_str)
