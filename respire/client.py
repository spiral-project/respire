from urllib import urlencode
from urlparse import urljoin
import json

import requests
from easydict import EasyDict


def client_from_url(url, session=requests):
    """Builds a client from an url

    :param url: the url you want to get the SPORE schema from
    :param session: the :class:`request.Session` instance to use. Defaults to
                    the requests module itself.

    """
    schema = session.get(url).json()
    return Client(description=schema, session=session)


def make_spore_function(client, method_definition):
    """Returns the actual function being exposed to the end user.

    :param client:
        the :class:`Client` instance to which the function will be bounded.

    :param method_definition:
        Definition of the method we are defining the function.
    """
    def spore_function(raise_for_status=True, **method_kw):
        return client.call_spore_function(
            method_definition, raise_for_status, **method_kw
        )

    spore_function.__doc__ = get_method_documentation(method_definition)
    return spore_function


def decode_response(resp, definition):
    """Decode the response if we know how to handle it"""
    if hasattr(resp, 'json'):
        return resp.json()
    else:
        return resp.body


def define_format(kw, definition):
    """Set the correct Content-Type headers and encode the data to the right
    format, if we know how to handle it.
    """
    if 'json' in definition.formats:
        if 'headers' not in kw or 'Content-Type' not in kw['headers']:
            kw['headers'] = {'Content-Type': 'application/json'}

        if 'data' in kw:
            kw['data'] = json.dumps(kw['data'])
    # XXX deal with other formats


def get_method_documentation(definition):
    """Get the documentation from the SPORE format and attach it to the method
    that will be exposed to the user.

    :param definition: the definition of the method, from the SPORE file.
    """
    if 'description' not in definition:
        definition['description'] = ''

    documentation = """
{description}

This binds to the {path} method.
Output format is in {formats}.
""".format(**definition)
    return documentation


class Client(object):
    """The way to interact with the API.

    :param description:
        a python object containing the definition of the SPORE service

    :param session:
        a :class:`requests.Session` instance that will be used to perform the
        http requests.

    This client provides two main things: the description, available as
    a dotted dict, and a number of methods to interact with the service.
    """

    def __init__(self, description, session=None):
        self.description = EasyDict(description)
        if session is None:
            session = requests
        self.session = session

        # for each method defined in the spore file, create a method on this
        # object.
        for method, definition in self.description.methods.items():
            spore_function = make_spore_function(self, definition)
            spore_function.__name__ = method
            setattr(self, method, spore_function)

    def call_spore_function(self, definition,
                            raise_for_status=True, **method_kw):
        """
        Handles the actual call to the resource and define for you some
        additional headers and behaviour depending on the spore definition
        that was given.

        :param method_definition:
            Definition of the method we are defining the function.

        :param service_description:
            SPORE description of the service. Could be useful to get top-level
            information, such as the base url of the service.
        """
        # for each param passed to the method,
        # match if it's needed in the path, and replace it there if
        # needed
        path = definition.path
        for kw in method_kw.keys():
            key = ':%s' % kw
            if key in path and kw != 'data':
                path = path.replace(key, method_kw.pop(kw))

        url = urljoin(self.description.base_url, path)

        define_format(method_kw, definition)

        if definition.method == 'DELETE' and 'data' in method_kw:
            data = method_kw.pop('data')
            data = json.loads(data)
            url += '?%s' % urlencode(data)

        # make the actual query to the resource
        resp = self.session.request(definition.method, url, **method_kw)
        if raise_for_status:
            resp.raise_for_status()

        return decode_response(resp, definition)
