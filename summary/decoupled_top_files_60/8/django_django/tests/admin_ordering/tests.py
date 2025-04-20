from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.models import User
from django.db.models import F
from django.test import RequestFactory, TestCase

from .models import (
    Band, DynOrderingBandAdmin, Song, SongInlineDefaultOrdering,
    SongInlineNewOrdering,
)


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True

    def has_module_perms(self, module):
        return True


request = MockRequest()
request.user = MockSuperUser()

site = admin.AdminSite()


class TestAdminOrdering(TestCase):
    """
    Let's make sure that ModelAdmin.get_queryset uses the ordering we define
    in ModelAdmin rather that ordering defined in the model's inner Meta
    class.
    """
    request_factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData is a class method used for setting up test data for a Django test case. It is called once before any test method is run. The method takes no parameters and does not return any value.
        
        Key Details:
        - Purpose: To create and store test data in the database.
        - Data Created: Three Band objects with the following attributes:
        - name: 'Aerosmith', 'Radiohead', 'Van Halen'
        - bio: An empty string
        - rank:
        """

        Band.objects.bulk_create([
            Band(name='Aerosmith', bio='', rank=3),
            Band(name='Radiohead', bio='', rank=1),
            Band(name='Van Halen', bio='', rank=2),
        ])

    def test_default_ordering(self):
        """
        The default ordering should be by name, as specified in the inner Meta
        class.
        """
        ma = ModelAdmin(Band, site)
        names = [b.name for b in ma.get_queryset(request)]
        self.assertEqual(['Aerosmith', 'Radiohead', 'Van Halen'], names)

    def test_specified_ordering(self):
        """
        Let's use a custom ModelAdmin that changes the ordering, and make sure
        it actually changes.
        """
        class BandAdmin(ModelAdmin):
            ordering = ('rank',)  # default ordering is ('name',)
        ma = BandAdmin(Band, site)
        names = [b.name for b in ma.get_queryset(request)]
        self.assertEqual(['Radiohead', 'Van Halen', 'Aerosmith'], names)

    def test_specified_ordering_by_f_expression(self):
        class BandAdmin(ModelAdmin):
            ordering = (F('rank').desc(nulls_last=True),)
        band_admin = BandAdmin(Band, site)
        names = [b.name for b in band_admin.get_queryset(request)]
        self.assertEqual(['Aerosmith', 'Van Halen', 'Radiohead'], names)

    def test_dynamic_ordering(self):
        """
        Let's use a custom ModelAdmin that changes the ordering dynamically.
        """
        super_user = User.objects.create(username='admin', is_superuser=True)
        other_user = User.objects.create(username='other')
        request = self.request_factory.get('/')
        request.user = super_user
        ma = DynOrderingBandAdmin(Band, site)
        names = [b.name for b in ma.get_queryset(request)]
        self.assertEqual(['Radiohead', 'Van Halen', 'Aerosmith'], names)
        request.user = other_user
        names = [b.name for b in ma.get_queryset(request)]
        self.assertEqual(['Aerosmith', 'Radiohead', 'Van Halen'], names)


class TestInlineModelAdminOrdering(TestCase):
    """
    Let's make sure that InlineModelAdmin.get_queryset uses the ordering we
    define in InlineModelAdmin.
    """

    @classmethod
    def setUpTestData(cls):
        cls.band = Band.objects.create(name='Aerosmith', bio='', rank=3)
        Song.objects.bulk_create([
            Song(band=cls.band, name='Pink', duration=235),
            Song(band=cls.band, name='Dude (Looks Like a Lady)', duration=264),
            Song(band=cls.band, name='Jaded', duration=214),
        ])

    def test_default_ordering(self):
        """
        The default ordering should be by name, as specified in the inner Meta
        class.
        """
        inline = SongInlineDefaultOrdering(self.band, site)
        names = [s.name for s in inline.get_queryset(request)]
        self.assertEqual(['Dude (Looks Like a Lady)', 'Jaded', 'Pink'], names)

    def test_specified_ordering(self):
        """
        Let's check with ordering set to something different than the default.
        """
        inline = SongInlineNewOrdering(self.band, site)
        names = [s.name for s in inline.get_queryset(request)]
        self.assertEqual(['Jaded', 'Pink', 'Dude (Looks Like a Lady)'], names)


class TestRelatedFieldsAdminOrdering(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.b1 = Band.objects.create(name='Pink Floyd', bio='', rank=1)
        cls.b2 = Band.objects.create(name='Foo Fighters', bio='', rank=5)

    def setUp(self):
        # we need to register a custom ModelAdmin (instead of just using
        # ModelAdmin) because the field creator tries to find the ModelAdmin
        # for the related model
        class SongAdmin(admin.ModelAdmin):
            pass
        site.register(Song, SongAdmin)

    def tearDown(self):
        """
        Method to clean up the Django site registry after tests. This method unregisters the 'Song' model and, if present, the 'Band' model from the Django site registry. This is typically used in test cases to ensure that the registry is in a known state after each test.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        Django site registry, model unregistration, test teardown
        
        Note:
        This method should be called in the tearDown method of Django test cases to ensure that
        """

        site.unregister(Song)
        if Band in site._registry:
            site.unregister(Band)

    def check_ordering_of_field_choices(self, correct_ordering):
        fk_field = site._registry[Song].formfield_for_foreignkey(Song.band.field, request=None)
        m2m_field = site._registry[Song].formfield_for_manytomany(Song.other_interpreters.field, request=None)
        self.assertEqual(list(fk_field.queryset), correct_ordering)
        self.assertEqual(list(m2m_field.queryset), correct_ordering)

    def test_no_admin_fallback_to_model_ordering(self):
        # should be ordered by name (as defined by the model)
        self.check_ordering_of_field_choices([self.b2, self.b1])

    def test_admin_with_no_ordering_fallback_to_model_ordering(self):
        class NoOrderingBandAdmin(admin.ModelAdmin):
            pass
        site.register(Band, NoOrderingBandAdmin)

        # should be ordered by name (as defined by the model)
        self.check_ordering_of_field_choices([self.b2, self.b1])

    def test_admin_ordering_beats_model_ordering(self):
        """
        Test the ordering of admin field choices when a ModelAdmin's ordering is set to a field, overriding the model's default ordering.
        
        This function registers a model with a custom ModelAdmin that sets the ordering to a specific field. It then checks the ordering of the field choices in the admin interface to ensure they are ordered according to the ModelAdmin's settings.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function is used for testing and does not return any value.
        
        Key
        """

        class StaticOrderingBandAdmin(admin.ModelAdmin):
            ordering = ('rank',)
        site.register(Band, StaticOrderingBandAdmin)

        # should be ordered by rank (defined by the ModelAdmin)
        self.check_ordering_of_field_choices([self.b1, self.b2])

    def test_custom_queryset_still_wins(self):
        """Custom queryset has still precedence (#21405)"""
        class SongAdmin(admin.ModelAdmin):
            # Exclude one of the two Bands from the querysets
            def formfield_for_foreignkey(self, db_field, request, **kwargs):
                """
                Generate a form field for a foreign key relationship.
                
                This method customizes the form field for a foreign key named 'band'. It filters the queryset to include only bands with a rank greater than 2. The method then calls the superclass's formfield_for_foreignkey method to generate the form field with the modified queryset.
                
                Parameters:
                db_field (django.db.models.Field): The foreign key field being processed.
                request (HttpRequest): The HTTP request object.
                **kwargs: Additional keyword arguments to
                """

                if db_field.name == 'band':
                    kwargs["queryset"] = Band.objects.filter(rank__gt=2)
                return super().formfield_for_foreignkey(db_field, request, **kwargs)

            def formfield_for_manytomany(self, db_field, request, **kwargs):
                if db_field.name == 'other_interpreters':
                    kwargs["queryset"] = Band.objects.filter(rank__gt=2)
                return super().formfield_for_foreignkey(db_field, request, **kwargs)

        class StaticOrderingBandAdmin(admin.ModelAdmin):
            ordering = ('rank',)

        site.unregister(Song)
        site.register(Song, SongAdmin)
        site.register(Band, StaticOrderingBandAdmin)

        self.check_ordering_of_field_choices([self.b2])
