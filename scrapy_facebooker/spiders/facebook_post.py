import re
import scrapy

from bs4 import BeautifulSoup
from collections import OrderedDict
from scrapy_facebooker.faceblib.url import get_real_external_link
from html import unescape
from scrapy_facebooker.items import FacebookPost
from urllib.parse import urlencode, urljoin, unquote


class FacebookPostSpider(scrapy.Spider):
    name = 'facebook_post'
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
        # Get into target's page
        return scrapy.Request(
            '{top_url}/pg/{username}/posts'.format(
                top_url=self.top_url,
                username=self.target_username),
            callback=self._get_facebook_posts_ajax)

    def _get_facebook_posts_ajax(self, response):
        # Get Facebook posts ajax
        def get_fb_page_id():
            p = re.compile(r'page_id=(\d*)')
            search = re.search(p, str(response.body))
            return search.group(1)

        self.fb_page_id = get_fb_page_id()

        # Default cursor to fetch early Facebook posts
        cursor = ('{"timeline_cursor":"timeline_unit:1:0:04611686018427387904'
                  ':09223372036854775803:04611686018427387904",'
                  '"timeline_section_cursor":{},"has_next_page":true}')

        return scrapy.Request(self.create_fb_post_ajax_url(self.fb_page_id,
                                                           cursor),
                              callback=self._parse_fb_story_links)

    def _parse_fb_story_links(self, response):
        def get_next_cursor():
            html_resp_unicode_decoded = str(
                response.body.decode('unicode_escape'))
            # Search for next cursor
            cursor_regex = re.compile('cursor=(.+)&surface')
            search_result = re.search(cursor_regex, html_resp_unicode_decoded)

            if search_result:
                next_cursor = unquote(
                    bytes(search_result.group(1), 'utf-8').decode(
                        'unicode_escape'))
                return next_cursor
            raise Exception('next_cursor not found, please report this issue '
                            'to our GitHub issue tracker.')

        post_links = set(re.findall(
                        r'(\/story\.php\?story_fbid=\d+(?:&|&amp;)id=\d+)',
                        unescape(str(response.body.decode('utf-8')))))
        for post_link in post_links:
            yield scrapy.Request(urljoin('https://m.facebook.com', post_link),
                                 callback=self._parse_post)

        next_cursor = get_next_cursor()

        if re.search(next_cursor, response.url):
            # If current url contains `next_cursor`,
            # it means that this is the last cursor.
            yield
        else:
            yield scrapy.Request(self.create_fb_post_ajax_url(self.fb_page_id,
                                                              next_cursor),
                                 callback=self._parse_fb_story_links)

    def _parse_post(self, response):
        html = str(response.body)
        fpost = FacebookPost()
        soup = BeautifulSoup(html, 'html.parser')

        def get_post_date():
            # Post date in m.facebook.com/story.php usually wrapped with
            # `abbr` tag.
            # TODO: Convert to Datetime object instead of just a string.
            return soup.abbr.text

        def get_post_text():
            content_html = soup.find('div', class_='_5rgt _5nk5')

            if content_html:
                return content_html.get_text()
            else:
                # Usually if the content has no text, it's an attachment, like
                # links, etc.
                selector_to_attachment = soup.select(
                    'section["data-sigil=touchable '
                    'feed-story-share-attachment"]')[0]
                link_attachment_elements = selector_to_attachment.find_all(
                    'a',
                    href=re.compile(
                        '^https\:\/\/lm\.facebook\.com\/l\.php\?.+'))

                real_attachment_link = get_real_external_link(
                    link_attachment_elements[0]['href'])
                return real_attachment_link

        def get_page_title_from_post():
            return soup.select('h3._52jd._52jb strong a')[0].get_text()

        def get_number_of_shares():
            shares_htmls = soup.select('a span["data-sigil=feed-ufi-sharers"]')
            # Extract the number from `shares_text`
            if shares_htmls:
                shares_text = shares_htmls[0].get_text()
                number = re.search(re.compile('(\d+)'), shares_text)
                if number:
                    return number.group(1)
            return '0'

        fpost['username'] = self.target_username
        fpost['date'] = get_post_date()
        fpost['content'] = get_post_text()
        fpost['page_title'] = get_page_title_from_post()
        fpost['shares_number'] = get_number_of_shares()
        fpost['url'] = response.url

        return fpost

    @staticmethod
    def create_fb_post_ajax_url(fb_page_id, cursor,
                                surface='mobile_page_posts',
                                unit_count=9999999):
        """
        Create a facebook post ajax url

        :param fb_page_id:  Facebook page id of the facebook page.
        :surface:           Default to 'mobile_page_posts' which means
                            it will fetch the mobile facebook page post ajax.
                            To fetch the web version, use `www_page_posts`.
        :unit_count:        An integer, default to 9999999. This number used
                            to tell how many posts will be fetched.
        :return:            An facebook post ajax url.
        """
        post_url = 'https://m.facebook.com/pages_reaction_units/more'
        query_str = urlencode(OrderedDict(page_id=fb_page_id,
                                          cursor=cursor,
                                          surface='mobile_page_posts',
                                          unit_count=unit_count))

        return '{post_url}/?{query}'.format(post_url=post_url, query=query_str)
