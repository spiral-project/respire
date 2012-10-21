from urlparse import urljoin
import json

import requests
from easydict import EasyDict


def client_from_url(url):
    """Builds a client from an url

    :param url: the url you want to get the SPORE schema from

    """
    schema = requests.get(url).json
    return Client(description=schema)


def make_spore_function(definition, description):
    def spore_function(raise_for_status=True, **method_kw):
        params = []
        for key in ('required_params', 'optional_params'):
            if hasattr(definition, key):
                params.extend(definition[key])

        # now do the actual request
        path = definition.path

        # for each param passed to the method,
        # match if it's needed in the path, and replace it there if
        # needed
        for kw in method_kw.keys():
            key = ':%s' % kw
            if key in path:
                path.replace(key, method_kw.pop(kw))

        url = urljoin(description.base_url, path)
        if 'headers' not in method_kw\
            or 'Content-Type' not in method_kw['headers']:
            if definition.format == 'json':
                method_kw['headers'] = {'Content-Type': 'application/json'}
        if definition.format == 'json' and 'data' in method_kw:
            method_kw['data'] = json.dumps(method_kw['data'])

        resp = requests.request(definition.method, url, **method_kw)
        if raise_for_status:
            resp.raise_for_status()
        if resp.json:
            return resp.json
        return resp.body

    return spore_function


class Client(object):

    def __init__(self, description):
        self.description = EasyDict(description)

        # now we want to build the methods
        for method, definition in self.description.methods.items():
            spore_function = make_spore_function(definition, self.description)
            if 'description' not in definition:
                definition['description'] = ''

            documentation = """
{description}

This binds to the {path} method.
Output format is {format}.
""".format(**definition)

            spore_function.__doc__ = documentation
            setattr(self, method, spore_function)
