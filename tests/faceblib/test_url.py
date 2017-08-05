import unittest

from scrapy_facebooker.faceblib.url import (
    get_real_external_link,
    get_facebook_url_from_username
)


class FaceblibURLTest(unittest.TestCase):

    def test_get_real_external_link(self):
        result = get_real_external_link(
            'https://lm.facebook.com/l.php?u=http%3A%2F%2Fgoogle.com')
        self.assertEqual(result, 'http://google.com')

    def test_get_facebook_url_from_username(self):
        result = get_facebook_url_from_username('testUsername')
        self.assertEqual(result, 'https://m.facebook.com/testUsername')
