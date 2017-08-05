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
    return real_link[0]


def get_facebook_url_from_username(username):
    """
    Get Facebook url from Facebook page/user username.

    :param username:    Username of the facebook page.
    :return:            Facebook page url.
    """
    return '{base_url}/{username}'.format(base_url=FACEBOOK_MOBILE_BASE_URL,
                                          username=username)


def create_facebook_photo_url_from_photo_id(photo_id, username):
    """
    Create a Facebook url from photo id and the username that owns the photo
    id.

    :param photo_id: ID of the photo.
    :param username: The username that owns the photo id.
    """
    return '{base_url}/{username}/photos/{id}'.format(
        base_url=FACEBOOK_MOBILE_BASE_URL,
        username=username,
        id=photo_id)
