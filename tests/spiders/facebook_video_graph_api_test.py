import os
import unittest
import requests_mock

from scrapy_facebooker.spiders.facebook_video_graph_api import (
    FacebookVideoGraphSpider
)


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'fb_video_graph_api_test_files',
                        name)


with open(get_testfile_path('id-videos.json')) as iv:
    id_videos_resp = bytes(iv.read(), 'utf-8')

with open(get_testfile_path('id-comments.json')) as ic:
    id_comments_resp = bytes(ic.read(), 'utf-8')

with open(get_testfile_path('id-reactions.json')) as ir:
    id_reactions_resp = bytes(ir.read(), 'utf-8')


class FacebookVideoGraphTest(unittest.TestCase):

    def test_target_username_not_filled(self):
        exception_msg = '^`target_username` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookVideoGraphSpider(access_token='123')

    def test_access_token_not_filled(self):
        exception_msg = '^`access_token` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookVideoGraphSpider(target_username='testname')

    def test_fill_target_username_and_access_token(self):
        graph_video_spider = FacebookVideoGraphSpider(
            target_username='test',
            access_token='testAccessToken')

        self.assertEqual(graph_video_spider.target_username, 'test')
        self.assertEqual(graph_video_spider.access_token, 'testAccessToken')

    def test_parse(self):
        graph_video_spider = FacebookVideoGraphSpider(
            target_username='testUsername',
            access_token='testAccessToken')

        with requests_mock.Mocker() as m:
            m.get(
                'https://graph.facebook.com/v2.7/testUsername/videos'
                '?access_token=testAccessToken',
                content=id_videos_resp,
                headers={'content-type': 'json'})
            m.get(
                'https://graph.facebook.com/v2.7/1/comments'
                '?access_token=testAccessToken',
                content=id_comments_resp,
                headers={'content-type': 'json'})
            m.get(
                'https://graph.facebook.com/v2.7/1/reactions'
                '?access_token=testAccessToken',
                content=id_reactions_resp,
                headers={'content-type': 'json'})

            result = list(graph_video_spider.parse(''))
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
                    'description': 'Video description',
                    'fb_id': '1',
                    'fb_video_url':
                        'https://web.facebook.com/testUsername/videos/1',
                    'reactions': [
                        {'id': '61', 'name': 'Irvan', 'type': 'LIKE'},
                        {'id': '62', 'name': 'Raymond', 'type': 'WOW'},
                        {'id': '63', 'name': 'Ida', 'type': 'HAHA'}],
                    'reactions_num': 3,
                    'updated_time': '2016-09-11T00:24:34+0000'}]
            )
