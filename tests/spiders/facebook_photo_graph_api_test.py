import os
import unittest
import requests_mock

from scrapy.http.response import Response
from scrapy.http.request import Request
from scrapy_facebooker.spiders.facebook_photo_graph_api import (
    FacebookPhotoGraphSpider
)


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'fb_photo_graph_api_test_files',
                        name)


# Load the testfiles that will be used to mock the responses
with open(get_testfile_path('photos.json')) as p:
    photos_resp = bytes(p.read(), 'utf-8')

with open(get_testfile_path('photos-profile.json')) as pf:
    photos_profile_resp = bytes(pf.read(), 'utf-8')

with open(get_testfile_path('photos-tagged.json')) as pt:
    photos_tagged_resp = bytes(pt.read(), 'utf-8')

with open(get_testfile_path('photos-uploaded.json')) as pu:
    photos_uploaded_resp = bytes(pu.read(), 'utf-8')

with open(get_testfile_path('id-reactions.json')) as ir:
    id_reactions_resp = bytes(ir.read(), 'utf-8')

with open(get_testfile_path('id-comments.json')) as ic:
    id_comments_resp = bytes(ic.read(), 'utf-8')

with open(get_testfile_path('photo-page.html')) as pp:
    photo_page_html_resp = bytes(pp.read(), 'utf-8')


class FacebookPhotoGraphTest(unittest.TestCase):

    def test_target_username_not_filled(self):
        exception_msg = '^`target_username` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookPhotoGraphSpider(access_token='123')

    def test_access_token_not_filled(self):
        exception_msg = '^`access_token` argument must be filled$'
        with self.assertRaisesRegex(Exception, exception_msg):
            FacebookPhotoGraphSpider(target_username='testname')

    def test_fill_target_username_and_access_token(self):
        graph_photo_spider = FacebookPhotoGraphSpider(
            target_username='test',
            access_token='testAccessToken')

        self.assertEqual(graph_photo_spider.target_username, 'test')
        self.assertEqual(graph_photo_spider.access_token, 'testAccessToken')

    def test_get_fb_photo_list(self):
        graph_photo_spider = FacebookPhotoGraphSpider(
            target_username='testusername',
            access_token='testAccessToken'
        )

        with requests_mock.Mocker() as m:
            m.get('https://graph.facebook.com/v2.7/testusername/photos'
                  '?access_token=testAccessToken', content=photos_resp,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/testusername/photos/profile'
                  '?access_token=testAccessToken', content=photos_profile_resp,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/testusername/photos/tagged'
                  '?access_token=testAccessToken', content=photos_tagged_resp,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/testusername/photos/uploade'
                  'd?access_token=testAccessToken',
                  content=photos_uploaded_resp,
                  headers={'content-type': 'json'})

            result = graph_photo_spider.get_fb_photo_list()
            self.assertEqual(
                result,
                [{'created_time': '2016-04-10T12:47:36+0000', 'id': '1'},
                 {'created_time': '2016-04-10T12:47:36+0000', 'id': '9'},
                 {'created_time': '2016-04-10T12:47:36+0000', 'id': '2'},
                 {'created_time': '2015-06-13T13:46:37+0000', 'id': '3'},
                 {'created_time': '2012-03-03T08:07:17+0000', 'id': '4'},
                 {'created_time': '2011-12-21T06:15:54+0000', 'id': '5'},
                 {'created_time': '2016-06-09T13:31:35+0000',
                  'name': 'Welcome to scrapy_facebooker!', 'id': '6'},
                 {'created_time': '2016-05-27T04:43:20+0000',
                  'name': 'This is a test name', 'id': '7'},
                 {'created_time': '2016-05-24T13:30:08+0000', 'id': '8'}])

    def test_parse(self):
        graph_photo_spider = FacebookPhotoGraphSpider(
            target_username='testUsername',
            access_token='testAccessToken'
        )

        # created_time and some other metadata are placed in the Request object
        req = Request('https://m.facebook.com/testUsername/1',
                      meta={'id': '1',
                            'created_time': '2016-04-10T12:47:36+0000',
                            'name': 'This is a name text'})
        resp = Response('https://m.facebook.com/testUsername/1',
                        body=photo_page_html_resp,
                        request=req)

        with requests_mock.Mocker() as m:
            # Mock the reactions and comments graph api request response.
            m.get('https://graph.facebook.com/v2.7/1/reactions'
                  '?access_token=testAccessToken',
                  content=id_reactions_resp, headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/1/comments'
                  '?access_token=testAccessToken',
                  content=id_comments_resp, headers={'content-type': 'json'})

            result = graph_photo_spider.parse(resp)
            self.assertEqual(
                result,
                {'comments': [{'created_time': '2017-07-20T03:18:29+0000',
                               'from': {'id': '1234568', 'name': 'People B'},
                               'id': '123456',
                               'message': 'comment1'},
                              {'created_time': '2017-07-19T13:43:14+0000',
                               'from': {'id': '1234567', 'name': 'People A'},
                               'id': '123456',
                               'message': 'comment2'}],
                    'comments_num': 2,
                    'created_time': '2016-04-10T12:47:36+0000',
                    'fb_id': '1',
                    'image_url': 'https://justexampleurl.com/test.jpg',
                    'name': 'This is a name text',
                    'reactions': [
                        {'id': '61', 'name': 'Irvan', 'type': 'LIKE'},
                        {'id': '62', 'name': 'Raymond', 'type': 'WOW'},
                        {'id': '63', 'name': 'Ida', 'type': 'HAHA'}],
                    'reactions_num': 3,
                    'url': 'https://m.facebook.com/testUsername/1'}
            )
