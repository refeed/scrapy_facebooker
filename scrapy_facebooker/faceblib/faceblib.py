import re
import requests

from scrapy_facebooker.faceblib.url import get_facebook_url_from_username


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
