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
        """
        Function: test_empty_https_proxy
        
        This function tests the behavior of a GET request when an empty string is provided as the HTTPS proxy.
        
        Parameters:
        - self: The test case object (unittest.TestCase).
        
        Returns:
        - None: The function asserts the status code of the response.
        
        Key Parameters:
        - proxy: A dictionary specifying the proxy settings. The key "https" is set to an empty string.
        
        Keywords:
        - smoke_url: The URL used for the GET request.
        - verify: A boolean flag
        """

        proxy = {"https" : "" }
        result = requests.get(self.smoke_url, verify=False, proxies = proxy)
        self.assertEqual(result.status_code, 200)

    def test_empty_http_proxy(self):
        proxy = {"http" : "" }
        result = requests.get(self.smoke_url, proxies = proxy)
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
