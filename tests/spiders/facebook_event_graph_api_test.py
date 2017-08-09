import os
import unittest
import requests_mock

from scrapy_facebooker.spiders.facebook_event_graph_api import (
    FacebookEventGraphSpider
)


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'fb_event_graph_api_test_files',
                        name)


with open(get_testfile_path('id-events.json')) as ie:
    id_events_resp = bytes(ie.read(), 'utf-8')

with open(get_testfile_path('id-comments.json')) as ic:
    id_comments_resp = bytes(ic.read(), 'utf-8')


class FacebookEventGraphTest(unittest.TestCase):

    def test_target_username_not_filled(self):
        exception_msg = '^`target_username` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookEventGraphSpider(access_token='123')

    def test_access_token_not_filled(self):
        exception_msg = '^`access_token` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookEventGraphSpider(target_username='testname')

    def test_fill_target_username_and_access_token(self):
        graph_event_spider = FacebookEventGraphSpider(
            target_username='test',
            access_token='testAccessToken')

        self.assertEqual(graph_event_spider.target_username, 'test')
        self.assertEqual(graph_event_spider.access_token, 'testAccessToken')

    def test_parse(self):
        graph_event_spider = FacebookEventGraphSpider(
            target_username='testUsername',
            access_token='testAccessToken')

        with requests_mock.Mocker() as m:
            m.get(
                'https://graph.facebook.com/v2.7/testUsername/events'
                '?access_token=testAccessToken',
                content=id_events_resp,
                headers={'content-type': 'json'})
            m.get(
                'https://graph.facebook.com/v2.7/1/comments'
                '?access_token=testAccessToken',
                content=id_comments_resp,
                headers={'content-type': 'json'})

            result = list(graph_event_spider.parse('b'))
            self.assertEqual(
                result,
                [{'comments': [{'created_time': '2017-07-20T03:18:29+0000',
                                'from': {'id': '1234568', 'name': 'People B'},
                                'id': '123456',
                                'message': 'comment1'},
                               {'created_time': '2017-07-19T13:43:14+0000',
                                'from': {'id': '1234567', 'name': 'People A'},
                                'id': '123456',
                                'message': 'comment2'}],
                    'comments_num': 2,
                    'description': 'An event about nothing',
                    'end_time': '2017-08-13T14:00:00+0700',
                    'fb_id': '1',
                    'name': 'scrapy_facebooker developers meeting',
                    'place': {'name': 'Earth'},
                    'start_time': '2017-08-13T10:00:00+0700',
                    'url': 'https://web.facebook.com/events/1'}])
