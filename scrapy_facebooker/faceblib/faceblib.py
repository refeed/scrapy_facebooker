import re
import requests

from urllib.parse import urlparse, parse_qs


FACEBOOK_MOBILE_BASE_URL = 'https://m.facebook.com'


def get_real_external_link(fb_encoded_link):
    """
    Get real external link from Facebook encoded link.

    :param fb_encoded_link: Facebook encoded link, usually starts with
                            "lm.facebook.com/l.php..."
    :return:                Real link of Facebook's encoded link.
    """
    parsed = urlparse(fb_encoded_link)
    real_link = parse_qs(parsed.query)['u']
    return real_link


def get_facebook_page_id(username):
    """
    Get Facebook page id

    :param username:  Username of the facebook page that its page id will be
                      fetched.
    :return:          Facebook page id.
    """
    html_page_resp_str = str(
        requests.get(get_facebook_url_from_username(username)).content)

    page_id_regex = re.compile(r'page_id\.(\d+)')
    search = re.search(page_id_regex, str(html_page_resp_str))

    return search.group(1)


def get_facebook_url_from_username(username):
    """
    Get Facebook url from Facebook page/user username.

    :param username:    Username of the facebook page.
    :return:            Facebook page url.
    """
    return '{base_url}/{username}'.format(base_url=FACEBOOK_MOBILE_BASE_URL,
                                          username=username)
