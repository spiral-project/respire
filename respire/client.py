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


def make_spore_function(method_definition, service_description):
    """Returns the actual function being exposed to the end user.

    Handles the actual call to the resource and define for you some
    additional headers and behaviour depending on the spore definition that was
    given.

    :param method_definition:
        Definition of the method we are defining the function.

    :param service_description:
        SPORE description of the service. Could be useful to get top-level
        information, such as the base url of the service.
    """
    # We need this level of indirection to handle the closures the right way.
    # That's because we're defining the functions sometimes in a loop, and here
    # we're defining a stack level for the passed arguments.
    def spore_function(raise_for_status=True, **method_kw):
        # for each param passed to the method,
        # match if it's needed in the path, and replace it there if
        # needed
        path = method_definition.path
        for kw in method_kw.keys():
            key = ':%s' % kw
            if key in path:
                path = path.replace(key, method_kw.pop(kw))

        url = urljoin(service_description.base_url, path)

        define_format(method_kw, method_definition)

        # make the actual query to the resource
        resp = requests.request(method_definition.method, url, **method_kw)
        if raise_for_status:
            resp.raise_for_status()

        return decode_response(resp, method_definition)

    spore_function.__doc__ = get_method_documentation(method_definition)
    return spore_function


def decode_response(resp, definition):
    """Decode the response if we know how to handle it"""
    if hasattr(resp, 'json'):
        return resp.json
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

    This client provides two main things: the description, available as
    a dotted dict, and a number of methods to interact with the service.
    """

    def __init__(self, description):
        self.description = EasyDict(description)

        # for each method defined in the spore file, create a method on this
        # object.
        for method, definition in self.description.methods.items():
            spore_function = make_spore_function(definition, self.description)
            spore_function.__name__ = method
            setattr(self, method, spore_function)
