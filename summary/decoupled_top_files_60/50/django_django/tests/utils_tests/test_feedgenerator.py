import datetime

from django.test import SimpleTestCase
from django.utils import feedgenerator
from django.utils.timezone import get_fixed_timezone, utc


class FeedgeneratorTests(SimpleTestCase):
    """
    Tests for the low-level syndication feed framework.
    """

    def test_get_tag_uri(self):
        """
        get_tag_uri() correctly generates TagURIs.
        """
        self.assertEqual(
            feedgenerator.get_tag_uri('http://example.org/foo/bar#headline', datetime.date(2004, 10, 25)),
            'tag:example.org,2004-10-25:/foo/bar/headline')

    def test_get_tag_uri_with_port(self):
        """
        get_tag_uri() correctly generates TagURIs from URLs with port numbers.
        """
        self.assertEqual(
            feedgenerator.get_tag_uri(
                'http://www.example.org:8000/2008/11/14/django#headline',
                datetime.datetime(2008, 11, 14, 13, 37, 0),
            ),
            'tag:www.example.org,2008-11-14:/2008/11/14/django/headline')

    def test_rfc2822_date(self):
        """
        rfc2822_date() correctly formats datetime objects.
        """
        self.assertEqual(
            feedgenerator.rfc2822_date(datetime.datetime(2008, 11, 14, 13, 37, 0)),
            "Fri, 14 Nov 2008 13:37:00 -0000"
        )

    def test_rfc2822_date_with_timezone(self):
        """
        rfc2822_date() correctly formats datetime objects with tzinfo.
        """
        self.assertEqual(
            feedgenerator.rfc2822_date(datetime.datetime(2008, 11, 14, 13, 37, 0, tzinfo=get_fixed_timezone(60))),
            "Fri, 14 Nov 2008 13:37:00 +0100"
        )

    def test_rfc2822_date_without_time(self):
        """
        rfc2822_date() correctly formats date objects.
        """
        self.assertEqual(
            feedgenerator.rfc2822_date(datetime.date(2008, 11, 14)),
            "Fri, 14 Nov 2008 00:00:00 -0000"
        )

    def test_rfc3339_date(self):
        """
        rfc3339_date() correctly formats datetime objects.
        """
        self.assertEqual(
            feedgenerator.rfc3339_date(datetime.datetime(2008, 11, 14, 13, 37, 0)),
            "2008-11-14T13:37:00Z"
        )

    def test_rfc3339_date_with_timezone(self):
        """
        rfc3339_date() correctly formats datetime objects with tzinfo.
        """
        self.assertEqual(
            feedgenerator.rfc3339_date(datetime.datetime(2008, 11, 14, 13, 37, 0, tzinfo=get_fixed_timezone(120))),
            "2008-11-14T13:37:00+02:00"
        )

    def test_rfc3339_date_without_time(self):
        """
        rfc3339_date() correctly formats date objects.
        """
        self.assertEqual(
            feedgenerator.rfc3339_date(datetime.date(2008, 11, 14)),
            "2008-11-14T00:00:00Z"
        )

    def test_atom1_mime_type(self):
        """
        Atom MIME type has UTF8 Charset parameter set
        """
        atom_feed = feedgenerator.Atom1Feed("title", "link", "description")
        self.assertEqual(
            atom_feed.content_type, "application/atom+xml; charset=utf-8"
        )

    def test_rss_mime_type(self):
        """
        RSS MIME type has UTF8 Charset parameter set
        """
        rss_feed = feedgenerator.Rss201rev2Feed("title", "link", "description")
        self.assertEqual(
            rss_feed.content_type, "application/rss+xml; charset=utf-8"
        )

    # Two regression tests for #14202

    def test_feed_without_feed_url_gets_rendered_without_atom_link(self):
        """
        Tests that a feed without a feed URL does not get rendered with an atom link.
        
        This function checks that when a feed is created without a feed URL, the generated feed content does not include an atom link, and does not contain any references to a feed URL in the output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function creates a feed using the Rss201rev2Feed class from the feedgenerator module.
        - The feed is initialized with a title
        """

        feed = feedgenerator.Rss201rev2Feed('title', '/link/', 'descr')
        self.assertIsNone(feed.feed['feed_url'])
        feed_content = feed.writeString('utf-8')
        self.assertNotIn('<atom:link', feed_content)
        self.assertNotIn('href="/feed/"', feed_content)
        self.assertNotIn('rel="self"', feed_content)

    def test_feed_with_feed_url_gets_rendered_with_atom_link(self):
        feed = feedgenerator.Rss201rev2Feed('title', '/link/', 'descr', feed_url='/feed/')
        self.assertEqual(feed.feed['feed_url'], '/feed/')
        feed_content = feed.writeString('utf-8')
        self.assertIn('<atom:link', feed_content)
        self.assertIn('href="/feed/"', feed_content)
        self.assertIn('rel="self"', feed_content)

    def test_atom_add_item(self):
        # Not providing any optional arguments to Atom1Feed.add_item()
        feed = feedgenerator.Atom1Feed('title', '/link/', 'descr')
        feed.add_item('item_title', 'item_link', 'item_description')
        feed.writeString('utf-8')

    def test_deterministic_attribute_order(self):
        """
        Tests the deterministic order of attributes in an Atom1Feed object's generated content.
        
        This function creates an Atom1Feed object with specified title, link, and description. It then generates the feed content as a UTF-8 string and checks if the link attribute is correctly formatted and included in the generated content.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        feedgenerator.Atom1Feed: The Atom1Feed object used to generate the feed content.
        feed.writeString('utf-8
        """

        feed = feedgenerator.Atom1Feed('title', '/link/', 'desc')
        feed_content = feed.writeString('utf-8')
        self.assertIn('href="/link/" rel="alternate"', feed_content)

    def test_latest_post_date_returns_utc_time(self):
        for use_tz in (True, False):
            with self.settings(USE_TZ=use_tz):
                rss_feed = feedgenerator.Rss201rev2Feed('title', 'link', 'description')
                self.assertEqual(rss_feed.latest_post_date().tzinfo, utc)
