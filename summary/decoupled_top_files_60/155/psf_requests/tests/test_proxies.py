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
        Tests the behavior of the `requests.get` function when an empty HTTPS proxy is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `proxy`: A dictionary specifying the proxy settings. In this case, it contains only an empty string for the HTTPS proxy.
        
        Keywords:
        - `requests.get`: The function used to send a GET request to the specified URL.
        - `self.smoke_url`: The URL to which the GET request is sent.
        - `
        """

        proxy = {"https" : "" }
        result = requests.get(self.smoke_url, verify=False, proxies = proxy)
        self.assertEqual(result.status_code, 200)

    def test_empty_http_proxy(self):
        """
        Test function to check the behavior of the requests.get method when an empty HTTP proxy is provided.
        
        Parameters:
        proxy (dict): A dictionary containing the HTTP proxy configuration. In this case, the HTTP proxy is set to an empty string.
        smoke_url (str): The URL to which the GET request is sent.
        
        Returns:
        int: The status code of the HTTP response.
        
        Key Points:
        - The function sends a GET request to the specified URL using the provided proxy configuration.
        - The proxy
        """

        proxy = {"http" : "" }
        result = requests.get(self.smoke_url, proxies = proxy)
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
