from django.contrib.syndication import views
from django.utils import feedgenerator
from django.utils.timezone import get_fixed_timezone

from .models import Article, Entry


class TestRss2Feed(views.Feed):
    title = 'My blog'
    description = 'A more thorough description of my blog.'
    link = '/blog/'
    feed_guid = '/foo/bar/1234'
    author_name = 'Sally Smith'
    author_email = 'test@example.com'
    author_link = 'http://www.example.com/'
    categories = ('python', 'django')
    feed_copyright = 'Copyright (c) 2007, Sally Smith'
    ttl = 600

    def items(self):
        return Entry.objects.all()

    def item_description(self, item):
        return "Overridden description: %s" % item

    def item_pubdate(self, item):
        return item.published

    def item_updateddate(self, item):
        return item.updated

    item_author_name = 'Sally Smith'
    item_author_email = 'test@example.com'
    item_author_link = 'http://www.example.com/'
    item_categories = ('python', 'testing')
    item_copyright = 'Copyright (c) 2007, Sally Smith'


class TestRss2FeedWithGuidIsPermaLinkTrue(TestRss2Feed):
    def item_guid_is_permalink(self, item):
        return True


class TestRss2FeedWithGuidIsPermaLinkFalse(TestRss2Feed):
    def item_guid(self, item):
        return str(item.pk)

    def item_guid_is_permalink(self, item):
        return False


class TestRss091Feed(TestRss2Feed):
    feed_type = feedgenerator.RssUserland091Feed


class TestNoPubdateFeed(views.Feed):
    title = 'Test feed'
    link = '/feed/'

    def items(self):
        return Entry.objects.all()


class TestAtomFeed(TestRss2Feed):
    feed_type = feedgenerator.Atom1Feed
    subtitle = TestRss2Feed.description


class TestLatestFeed(TestRss2Feed):
    """
    A feed where the latest entry date is an `updated` element.
    """
    feed_type = feedgenerator.Atom1Feed
    subtitle = TestRss2Feed.description

    def items(self):
        return Entry.objects.exclude(pk=5)


class ArticlesFeed(TestRss2Feed):
    """
    A feed to test no link being defined. Articles have no get_absolute_url()
    method, and item_link() is not defined.
    """
    def items(self):
        return Article.objects.all()


class TestSingleEnclosureRSSFeed(TestRss2Feed):
    """
    A feed to test that RSS feeds work with a single enclosure.
    """
    def item_enclosure_url(self, item):
        return 'http://example.com'

    def item_enclosure_size(self, item):
        return 0

    def item_mime_type(self, item):
        return 'image/png'


class TestMultipleEnclosureRSSFeed(TestRss2Feed):
    """
    A feed to test that RSS feeds raise an exception with multiple enclosures.
    """
    def item_enclosures(self, item):
        """
        Generates enclosures for an RSS or Atom feed item.
        
        Args:
        item: The feed item to which the enclosures will be added.
        
        Returns:
        A list of `feedgenerator.Enclosure` objects representing the media content associated with the feed item.
        
        Example:
        >>> item_enclosures(item)
        [Enclosure('http://example.com/hello.png', 0, 'image/png'), Enclosure('http://example.com/goodbye.png', 0, '
        """

        return [
            feedgenerator.Enclosure('http://example.com/hello.png', 0, 'image/png'),
            feedgenerator.Enclosure('http://example.com/goodbye.png', 0, 'image/png'),
        ]


class TemplateFeed(TestRss2Feed):
    """
    A feed to test defining item titles and descriptions with templates.
    """
    title_template = 'syndication/title.html'
    description_template = 'syndication/description.html'

    # Defining a template overrides any item_title definition
    def item_title(self):
        return "Not in a template"


class TemplateContextFeed(TestRss2Feed):
    """
    A feed to test custom context data in templates for title or description.
    """
    title_template = 'syndication/title_context.html'
    description_template = 'syndication/description_context.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and modify the context data for a view.
        
        This method extends the functionality of the superclass's `get_context_data` method by adding a new key-value pair to the context dictionary. The key is 'foo' and the value is 'bar'.
        
        Args:
        **kwargs: Additional keyword arguments passed to the method.
        
        Returns:
        A dictionary containing the original context data with an additional key-value pair.
        """

        context = super().get_context_data(**kwargs)
        context['foo'] = 'bar'
        return context


class TestLanguageFeed(TestRss2Feed):
    language = 'de'


class NaiveDatesFeed(TestAtomFeed):
    """
    A feed with naive (non-timezone-aware) dates.
    """
    def item_pubdate(self, item):
        return item.published


class TZAwareDatesFeed(TestAtomFeed):
    """
    A feed with timezone-aware dates.
    """
    def item_pubdate(self, item):
        """
        Returns the published date of an item with a fixed timezone offset of 42 minutes. The input is an item object with a 'published' attribute containing a datetime object. The output is a datetime object with the specified timezone offset.
        """

        # Provide a weird offset so that the test can know it's getting this
        # specific offset and not accidentally getting on from
        # settings.TIME_ZONE.
        return item.published.replace(tzinfo=get_fixed_timezone(42))


class TestFeedUrlFeed(TestAtomFeed):
    feed_url = 'http://example.com/customfeedurl/'


class MyCustomAtom1Feed(feedgenerator.Atom1Feed):
    """
    Test of a custom feed generator class.
    """
    def root_attributes(self):
        """
        Generates root attributes for an object.
        
        This method extends the functionality of the superclass's `root_attributes` method by adding a new attribute 'django' with the value 'rocks'. The resulting dictionary of attributes is then returned.
        
        Args:
        None
        
        Returns:
        dict: A dictionary containing the root attributes, including the newly added 'django' attribute set to 'rocks'.
        """

        attrs = super().root_attributes()
        attrs['django'] = 'rocks'
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        handler.addQuickElement('spam', 'eggs')

    def item_attributes(self, item):
        """
        Generates item attributes with additional 'bacon' attribute set to 'yum'.
        
        This method extends the functionality of the base class's `item_attributes` method by adding an extra attribute 'bacon' with the value 'yum'. It then returns the updated dictionary of attributes.
        
        Args:
        item: The item for which the attributes are being generated.
        
        Returns:
        A dictionary containing the item's attributes, including the newly added 'bacon' attribute set to 'yum
        """

        attrs = super().item_attributes(item)
        attrs['bacon'] = 'yum'
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement('ministry', 'silly walks')


class TestCustomFeed(TestAtomFeed):
    feed_type = MyCustomAtom1Feed


class TestSingleEnclosureAtomFeed(TestAtomFeed):
    """
    A feed to test that Atom feeds work with a single enclosure.
    """
    def item_enclosure_url(self, item):
        return 'http://example.com'

    def item_enclosure_size(self, item):
        return 0

    def item_mime_type(self, item):
        return 'image/png'


class TestMultipleEnclosureAtomFeed(TestAtomFeed):
    """
    A feed to test that Atom feeds work with multiple enclosures.
    """
    def item_enclosures(self, item):
        """
        Generates enclosures for an RSS or Atom feed item.
        
        Args:
        item: The feed item to which the enclosures will be added.
        
        Returns:
        A list of `feedgenerator.Enclosure` objects representing the media content associated with the feed item.
        
        Example:
        >>> item_enclosures(None)
        [Enclosure('http://example.com/hello.png', '0', 'image/png'), Enclosure('http://example.com/goodbye.png', '0', '
        """

        return [
            feedgenerator.Enclosure('http://example.com/hello.png', '0', 'image/png'),
            feedgenerator.Enclosure('http://example.com/goodbye.png', '0', 'image/png'),
        ]
