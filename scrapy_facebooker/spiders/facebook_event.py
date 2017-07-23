import re
import scrapy

from bs4 import BeautifulSoup
from collections import OrderedDict
from scrapy_facebooker.items import FacebookEvent
from urllib.parse import urlencode, urljoin


class FacebookEventSpider(scrapy.Spider):
    name = 'facebook_event'
    start_urls = (
        'https://m.facebook.com/',
    )
    allowed_domains = ['m.facebook.com']
    top_url = 'https://m.facebook.com'

    def __init__(self, *args, **kwargs):
        self.target_username = kwargs.get('target_username')

        if not self.target_username:
            raise Exception('`target_username` argument must be filled')

    def parse(self, response):
        # Get into target's events page
        return scrapy.Request(
            '{top_url}/{username}/events'.format(
                top_url=self.top_url,
                username=self.target_username),
            callback=self._get_facebook_events_ajax)

    def _get_facebook_events_ajax(self, response):
        # Get Facebook events ajax
        def get_fb_page_id():
            p = re.compile(r'page_id=(\d*)')
            search = re.search(p, str(response.body))
            return search.group(1)

        self.fb_page_id = get_fb_page_id()

        return scrapy.Request(self.create_fb_event_ajax_url(self.fb_page_id,
                                                            '0',
                                                            'u_0_d'),
                              callback=self._get_fb_event_links)

    def _get_fb_event_links(self, response):
        html_resp_unicode_decoded = str(
            response.body.decode('unicode_escape')).replace('\\', '')

        def get_see_more_id():
            # Get the next see more id
            see_more_id_regex = re.compile(r'see_more_id=(\w+)&')
            see_more_id_search = re.search(see_more_id_regex,
                                           html_resp_unicode_decoded)
            if see_more_id_search:
                return see_more_id_search.group(1)
            return None

        def get_serialized_cursor():
            # Get the next serialized_cursor
            serialized_cursor_regex = re.compile(r'serialized_cursor=([\w-]+)')
            serialized_cursor_search = re.search(serialized_cursor_regex,
                                                 html_resp_unicode_decoded)
            if serialized_cursor_search:
                return serialized_cursor_search.group(1)
            return None

        # Extract event urls from fb event ajax response.
        event_url_regex = re.compile(r'href=\"(/events/\d+)')
        event_urls = set(
            re.findall(event_url_regex, html_resp_unicode_decoded)
        )
        for event_url in event_urls:
            yield scrapy.Request(urljoin(self.top_url, event_url),
                                 callback=self._parse_event)

        # Check if there are `serialized_cursor` and `see_more_id` attached in
        # the ajax response.
        next_serialized_cursor = get_serialized_cursor()
        next_see_more_id = get_see_more_id()
        if next_serialized_cursor and next_see_more_id:
            yield scrapy.Request(self.create_fb_event_ajax_url(
                self.fb_page_id,
                next_serialized_cursor,
                next_see_more_id),
                callback=self._get_fb_event_links)

    def _parse_event(self, response):
        html_str = str(response.body)
        soup = BeautifulSoup(html_str, 'html.parser')

        def get_event_summary():
            # Return an array containing two elements,
            # the first element is the date of the event,
            # the second element is the place of the event.
            summaries = soup.find('div', id='event_summary').findChildren(
                recursive=False
            )
            date_and_place_list = [element.get_text(' ') for element in
                                   summaries]
            # All events should have a date, but it's not necessary
            # to have a place, sometimes there's an event that doesn't
            # have a place.
            if len(date_and_place_list) != 2:
                date_and_place_list.append(None)
            return date_and_place_list

        def get_event_title():
            return soup.select('header h3')[0].get_text()

        def get_event_date():
            return soup.select('header span')[0]['title']

        fevent = FacebookEvent()
        fevent['username'] = self.target_username
        fevent['url'] = response.url
        fevent['summary_date'], fevent['summary_place'] = get_event_summary()
        fevent['title'] = get_event_title()
        fevent['date'] = get_event_date()
        return fevent

    @staticmethod
    def create_fb_event_ajax_url(page_id, serialized_cursor, see_more_id):
        event_url = 'https://m.facebook.com/pages/events/more'
        query_str = urlencode(OrderedDict(page_id=page_id,
                                          query_type='past',
                                          see_more_id=see_more_id,
                                          serialized_cursor=serialized_cursor))

        return '{event_url}/?{query}'.format(event_url=event_url,
                                             query=query_str)
