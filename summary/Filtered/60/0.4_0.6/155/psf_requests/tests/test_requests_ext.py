#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Path hack.
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import unittest

import requests
from requests.compat import is_py2, is_py3

try:
    import omnijson as json
except ImportError:
    import json


class RequestsTestSuite(unittest.TestCase):
    """Requests test cases."""

    # It goes to eleven.
    _multiprocess_can_split_ = True

    def test_addition(self):
        assert (1 + 1) == 2

    def test_ssl_hostname_ok(self):
        requests.get('https://github.com', verify=True)

    def test_ssl_hostname_not_ok(self):
        """
        Function to test SSL hostname validation.
        
        This function sends a GET request to 'https://kennethreitz.com' with SSL verification disabled and then attempts to catch a SSLError exception to verify that the hostname validation is not working as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        requests.exceptions.SSLError: If the SSL hostname validation is unexpectedly successful.
        
        Note:
        - The function uses the `requests` library to send the HTTP request.
        - SSL verification is
        """

        requests.get('https://kennethreitz.com', verify=False)

        self.assertRaises(requests.exceptions.SSLError, requests.get, 'https://kennethreitz.com')

    def test_ssl_hostname_session_not_ok(self):

        s = requests.session()

        self.assertRaises(requests.exceptions.SSLError, s.get, 'https://kennethreitz.com')

        s.get('https://kennethreitz.com', verify=False)

    def test_binary_post(self):
        '''We need to be careful how we build the utf-8 string since
        unicode literals are a syntax error in python3
        '''

        if is_py2:
            # Blasphemy!
            utf8_string = eval("u'Smörgås'.encode('utf-8')")
        elif is_py3:
            utf8_string = 'Smörgås'.encode('utf-8')
        else:
            raise EnvironmentError('Flesh out this test for your environment.')
        requests.post('http://www.google.com/', data=utf8_string)

    def test_unicode_error(self):
        url = 'http://blip.fm/~1abvfu'
        requests.get(url)

    def test_chunked_head_redirect(self):
        """
        Tests the HTTP HEAD request for a URL that uses chunked transfer encoding and follows redirects.
        
        Parameters:
        url (str): The URL to perform the HEAD request on.
        
        Returns:
        None: This function asserts that the status code of the response is 200.
        
        Key Behavior:
        - Sends a HEAD request to the specified URL.
        - Follows any redirects that occur during the request.
        - Asserts that the status code of the final response is 200.
        """

        url = "http://t.co/NFrx0zLG"
        r = requests.head(url, allow_redirects=True)
        self.assertEqual(r.status_code, 200)

    def test_unicode_redirect(self):
        '''This url redirects to a location that has a nonstandard
        character in it, that breaks requests in python2.7

        After some research, the cause was identified as an unintended
        sideeffect of overriding of str with unicode.

        In the case that the redirected url is actually a malformed
        "bytes" object, i.e. a string with character c where
            ord(c) > 127,
        then unicode(url) breaks.
        '''
        r = requests.get('http://www.marketwire.com/mw/release.' +
                         'do?id=1628202&sourceType=3')
        assert r.ok

    def test_unicode_url_outright(self):
        '''This url visits in my browser'''
        r = requests.get('http://www.marketwire.com/press-release/' +
                         'jp-morgan-behauptet-sich-der-spitze-euro' +
                         'p%C3%A4ischer-anleihe-analysten-laut-umf' +
                         'rageergebnissen-1628202.htm')
        assert r.ok

    def test_redirect_encoding(self):
        '''This url redirects to
        http://www.dealipedia.com/deal_view_investment.php?r=20012'''

        r = requests.get('http://feedproxy.google.com/~r/Dealipedia' +
                         'News/~3/BQtUJRJeZlo/deal_view_investment.' +
                         'php')
        assert r.ok

    def test_cookies_on_redirects(self):
        """Test interaction between cookie handling and redirection."""
        # get a cookie for tinyurl.com ONLY
        s = requests.session()
        s.get(url='http://tinyurl.com/preview.php?disable=1')
        # we should have set a cookie for tinyurl: preview=0
        self.assertTrue('preview' in s.cookies)
        self.assertEqual(s.cookies['preview'], '0')
        self.assertEqual(list(s.cookies)[0].name, 'preview')
        self.assertEqual(list(s.cookies)[0].domain, 'tinyurl.com')

        # get cookies on another domain
        r2 = s.get(url='http://httpbin.org/cookies')
        # the cookie is not there
        self.assertTrue('preview' not in json.loads(r2.text)['cookies'])

        # this redirects to another domain, httpbin.org
        # cookies of the first domain should NOT be sent to the next one
        r3 = s.get(url='http://tinyurl.com/7zp3jnr')
        assert r3.url == 'http://httpbin.org/cookies'
        self.assertTrue('preview' not in json.loads(r3.text)['cookies'])

if __name__ == '__main__':
    unittest.main()
