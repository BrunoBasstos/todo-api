# /tests/test_home.py
from tests.base import BaseTestCase


class TestHome(BaseTestCase):

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/openapi/swagger')
