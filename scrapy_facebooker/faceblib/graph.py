"""This module contains helper functions for `facebook` library"""

from urllib.parse import urlparse, parse_qs


def get_all_data_from_graph_api(fgraph, fb_obj, **kwargs):
    """
    Get all data from graph api.

    :param fgraph:  A `facebook.GraphAPI` instance.
    :param fb_obj:  (str) Object that will be fetched from Facebook Graph API.
    :return:        List of datas which are fetched from Facebook Graph API.
    """
    data_list = []
    graph_resp = fgraph.get_object(fb_obj, **kwargs)

    data_list.extend(graph_resp['data'])

    while 'paging' in graph_resp and 'next' in graph_resp['paging']:
        if 'cursors' in graph_resp['paging']:
            graph_resp = fgraph.get_object(
                fb_obj,
                after=graph_resp['paging']['cursors']['after'],
                **kwargs)
        else:
            # Extract parameters from the next paging graph API url
            queries = parse_qs(urlparse(graph_resp['paging']['next']).query)
            kwargs.update(queries)
            graph_resp = fgraph.get_object(
                fb_obj,
                **kwargs
            )
        data_list.extend(graph_resp['data'])

    return data_list
