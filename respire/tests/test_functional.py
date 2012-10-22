import json
import os
import unittest

from cornice.service import Service, get_services
from rxjson import Rx
from webtest import TestApp

from respire.tests import todo


HERE = os.path.dirname(os.path.abspath(__file__))


class FunctionalTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.app = TestApp(todo.main())
        self.headers = {'Content-Type': 'application/json'}
        return super(FunctionalTest, self).__init__(*args, **kwargs)

    def test_spore(self):
        rx = Rx.Factory({ "register_core_types": True })
        with open(os.path.join(HERE, 'spore_validation.rx')) as f:
            spore_json_schema = json.loads(f.read())
            spore_schema = rx.make_schema(spore_json_schema)
            resp = self.app.get('/spore', headers=self.headers)
            self.assertTrue(spore_schema.check(resp.json))
