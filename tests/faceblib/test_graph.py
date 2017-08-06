import facebook
import os
import requests_mock
import unittest

from scrapy_facebooker.faceblib.graph import get_all_data_from_graph_api


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'graph_testfiles',
                        name)


# Load the testfiles that will be used to mock responses
with open(get_testfile_path('apiresp.json')) as ar:
    with open(get_testfile_path('next_cursor_apiresp.json')) as next_ar:
        apiresp = bytes(ar.read(), 'utf-8')
        next_cursor_apiresp = bytes(next_ar.read(), 'utf-8')

with open(get_testfile_path('post_api_resp_with_no_cursor.json')) as arnc:
    post_api_resp_no_cursor = bytes(arnc.read(), 'utf-8')

with open(get_testfile_path('next_post_api_resp_with_no_cursor.json')) as nrnc:
    next_post_api_resp_no_cursor = bytes(nrnc.read(), 'utf-8')

with open(get_testfile_path('blank_data_resp.json')) as br:
    blank_data_resp = bytes(br.read(), 'utf-8')


class FaceblibGraphTest(unittest.TestCase):

    def test_get_all_data_from_graph_api(self):
        graph = facebook.GraphAPI(
            access_token='testAccessToken', version='2.7')

        with requests_mock.Mocker() as m:
            m.get('https://graph.facebook.com/v2.7/testusername/photos'
                  '?access_token=testAccessToken', content=apiresp,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/testusername/photos'
                  '?access_token=testAccessToken&after=afterCursor',
                  content=next_cursor_apiresp,
                  headers={'content-type': 'json'})

            result = get_all_data_from_graph_api(graph, 'testusername/photos')
            self.assertEqual(
                result,
                [{'created_time': '2016-04-10T12:47:36+0000', 'id': '1'},
                 {'created_time': '2016-05-10T12:47:36+0000', 'id': '2'},
                 {'created_time': '2016-06-10T12:47:36+0000', 'id': '3'},
                 {'created_time': '2016-07-10T12:47:36+0000', 'id': '4'},
                 {'created_time': '2016-08-10T12:47:36+0000', 'id': '5'}])

    def test_get_all_data_from_graph_api_with_no_cursor(self):
        # Test get_all_data_from_graph_api() with no cursor, but there's
        # a 'next' graph api url that provided by graph API.
        graph = facebook.GraphAPI(
            access_token='testAccessToken', version='2.7')

        with requests_mock.Mocker() as m:
            # Mock the Graph API responses.
            m.get('https://graph.facebook.com/v2.7/testusername/posts'
                  '?access_token=testAccessToken',
                  content=post_api_resp_no_cursor,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/testusername/posts?limit=25'
                  '&format=json&__paging_token=enc_samplePagingToken&until=133'
                  '0763197&access_token=testAccessToken',
                  content=next_post_api_resp_no_cursor,
                  headers={'content-type': 'json'})
            m.get('https://graph.facebook.com/v2.7/testusername/posts?limit=25'
                  '&format=json&__paging_token=enc_samplePagingTokenB&until=13'
                  '30763199&access_token=testAccessToken',
                  content=blank_data_resp,
                  headers={'content-type': 'json'})

            result = get_all_data_from_graph_api(graph, 'testusername/posts')
            self.assertEqual(
                result,
                [{'created_time': '2016-06-10T12:47:36+0000',
                  'id': '1', 'story': 'A story'},
                 {'created_time': '2016-07-10T12:47:36+0000',
                  'id': '2', 'story': 'of'},
                 {'created_time': '2016-08-10T12:47:36+0000',
                  'id': '3', 'story': 'Test Username added a link'},
                 {'created_time': '2016-06-10T12:47:36+0000',
                  'id': '4', 'story': 'Scrapy'},
                 {'created_time': '2016-07-10T12:47:36+0000',
                  'id': '5', 'story': 'Facebooker'},
                 {'created_time': '2016-08-10T12:47:36+0000',
                  'id': '6', 'story': 'Graph'}])
