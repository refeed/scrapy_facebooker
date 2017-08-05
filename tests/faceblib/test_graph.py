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
