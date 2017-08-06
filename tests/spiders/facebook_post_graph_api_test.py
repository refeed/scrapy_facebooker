import os
import requests_mock
import unittest

from scrapy_facebooker.spiders.facebook_post_graph_api import (
    FacebookPostGraphSpider)


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'fb_post_graph_api_test_files',
                        name)


# Load the testfiles that will be used to mock the responses
with open(get_testfile_path('id-posts.json')) as ip:
    id_posts_resp = bytes(ip.read(), 'utf-8')

with open(get_testfile_path('id-reactions.json')) as ir:
    id_reactions_resp = bytes(ir.read(), 'utf-8')

with open(get_testfile_path('id-comments.json')) as ic:
    id_comments_resp = bytes(ic.read(), 'utf-8')


class FacebookPostGraphSpiderTest(unittest.TestCase):

    def test_target_username_not_filled(self):
        exception_msg = '^`target_username` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookPostGraphSpider(access_token='123')

    def test_access_token_not_filled(self):
        exception_msg = '^`access_token` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookPostGraphSpider(target_username='testname')

    def test_fill_target_username_and_access_token(self):
        graph_post_spider = FacebookPostGraphSpider(
            target_username='test',
            access_token='testAccessToken')

        self.assertEqual(graph_post_spider.target_username, 'test')
        self.assertEqual(graph_post_spider.access_token, 'testAccessToken')

    def test_parse(self):
        graph_post_spider = FacebookPostGraphSpider(
            target_username='testUsername',
            access_token='testAccessToken')

        with requests_mock.Mocker() as m:
            m.get('https://graph.facebook.com/v2.7/testUsername/posts'
                  '?access_token=testAccessToken',
                  content=id_posts_resp,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/1_2/reactions'
                  '?access_token=testAccessToken',
                  content=id_reactions_resp,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/1_2/comments'
                  '?access_token=testAccessToken',
                  content=id_comments_resp,
                  headers={'content-type': 'json'})

            result = list(graph_post_spider.parse(''))
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
                    'created_time': '2016-06-10T12:47:36+0000',
                    'fb_id': '1_2',
                    'message': 'Hello scrapy_facebooker!',
                    'reactions': [{'id': '61', 'name': 'Irvan',
                                   'type': 'LIKE'},
                                  {'id': '62', 'name': 'Raymond',
                                   'type': 'WOW'},
                                  {'id': '63', 'name': 'Ida', 'type': 'HAHA'}],
                    'reactions_num': 3,
                    'story': 'A sample story',
                    'url': 'https://web.facebook.com/testUsername/posts/2'}])
