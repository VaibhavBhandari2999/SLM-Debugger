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
        Test function to check HTTP proxy functionality.
        
        This function tests the behavior of the requests library when an empty string is provided as the HTTP proxy.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        proxy (dict): A dictionary containing the HTTP proxy setting. The dictionary is expected to have a single key 'http' with an empty string as its value.
        
        Keywords:
        smoke_url (str): The URL used for the test request.
        
        Example:
        >>> test_empty_http_proxy()
        """

        proxy = {"http" : "" }
        result = requests.get(self.smoke_url, proxies = proxy)
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
