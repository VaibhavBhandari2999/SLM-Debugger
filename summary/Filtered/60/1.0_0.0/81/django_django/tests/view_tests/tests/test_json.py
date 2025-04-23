import json

from django.test import SimpleTestCase, override_settings


@override_settings(ROOT_URLCONF='view_tests.generic_urls')
class JsonResponseTests(SimpleTestCase):

    def test_json_response(self):
        """
        Tests the JSON response from the server.
        
        This function sends a GET request to the '/json/response/' endpoint and checks the response status code, content type, and the JSON content.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The response status code should be 200.
        - The content type of the response should be 'application/json'.
        - The JSON content of the response should match the expected dictionary:
        {
        'a': [1, 2
        """

        response = self.client.get('/json/response/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers['content-type'], 'application/json')
        self.assertEqual(json.loads(response.content.decode()), {
            'a': [1, 2, 3],
            'foo': {'bar': 'baz'},
            'timestamp': '2013-05-19T20:00:00',
            'value': '3.14',
        })
