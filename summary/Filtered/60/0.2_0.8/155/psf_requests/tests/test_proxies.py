#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, unittest

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
import requests


class HTTPSProxyTest(unittest.TestCase):
    """Smoke test for https functionality."""

    smoke_url = "https://github.com"

    def test_empty_https_proxy(self):
        proxy = {"https" : "" }
        result = requests.get(self.smoke_url, verify=False, proxies = proxy)
        self.assertEqual(result.status_code, 200)

    def test_empty_http_proxy(self):
        """
        Function: test_empty_http_proxy
        
        This function tests the HTTP request with an empty proxy setting.
        
        Parameters:
        - self: The object instance (typically used in unittest.TestCase).
        
        Returns:
        - None: The function asserts the status code of the HTTP response.
        
        Key Parameters:
        - proxy (dict): A dictionary specifying the HTTP proxy. In this case, it is set to an empty string for the "http" key.
        
        Keywords:
        - smoke_url (str): The URL used for the HTTP GET request.
        """

        proxy = {"http" : "" }
        result = requests.get(self.smoke_url, proxies = proxy)
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
