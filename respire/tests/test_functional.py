import json
import os
import requests
import unittest

from rxjson import Rx

from respire import client_from_url
from respire.tests import todo


HERE = os.path.dirname(os.path.abspath(__file__))


class FunctionalTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        # Requests
        self.spore_url = 'http://localhost:8080/spore'
        self.client = client_from_url(self.spore_url)
        return super(FunctionalTest, self).__init__(*args, **kwargs)

    def test_spore(self):
        """Test that the inputed spore is valid."""
        rx = Rx.Factory({ "register_core_types": True })
        with open(os.path.join(HERE, 'spore_validation.rx')) as f:
            spore_json_schema = json.loads(f.read())
            spore_schema = rx.make_schema(spore_json_schema)
            self.assertTrue(spore_schema.check(requests.get(self.spore_url).json))

    def test_get_todo_empty(self):
        """Test the first todo method."""
        result = self.client.get_todo()
        self.assertEqual(result, {})

    def test_get_todo_with_key(self):
        """Test the first todo method."""
        self.client.post_todo(data={'first': 'value'})
        
        result = self.client.get_todo()
        self.assertEqual(result, {'first': 'value'})

