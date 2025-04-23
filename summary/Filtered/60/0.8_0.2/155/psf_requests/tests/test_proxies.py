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
        - `proxy`: A dictionary specifying the proxy settings. In this case, it contains an empty string for the HTTPS proxy.
        
        Keywords:
        - `verify`: A boolean indicating whether SSL certificates should be verified. Set to `False` in this test.
        - `proxies`: A dictionary specifying the proxy settings for the request.
        
        Description
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
