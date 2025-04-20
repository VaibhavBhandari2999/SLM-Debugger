from django.test import TestCase

from .models import Flea, House, Person, Pet, Room


class UUIDPrefetchRelated(TestCase):

    def test_prefetch_related_from_uuid_model(self):
        """
        Tests the prefetch_related functionality with a UUID model.
        
        This function creates a Pet object and associates it with two Person objects. It then queries the database to fetch the Pet object along with its associated People using prefetch_related. The test ensures that the prefetch_related query is executed only once, and subsequent access to the related People does not result in additional database queries.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        """

        Pet.objects.create(name='Fifi').people.add(
            Person.objects.create(name='Ellen'),
            Person.objects.create(name='George'),
        )

        with self.assertNumQueries(2):
            pet = Pet.objects.prefetch_related('people').get(name='Fifi')
        with self.assertNumQueries(0):
            self.assertEqual(2, len(pet.people.all()))

    def test_prefetch_related_to_uuid_model(self):
        """
        Tests the prefetch_related functionality with a UUID model.
        
        This test checks the prefetch_related method on a Person model that has a many-to-many relationship with a Pet model. It ensures that the prefetching works correctly and that the number of database queries is minimized.
        
        Key Parameters:
        - None
        
        Keywords:
        - prefetch_related: Used to prefetch related objects from the database to avoid N+1 queries.
        - UUID model: The Pet model uses UUIDs for primary keys.
        
        Input:
        - None
        
        Output:
        -
        """

        Person.objects.create(name='Bella').pets.add(
            Pet.objects.create(name='Socks'),
            Pet.objects.create(name='Coffee'),
        )

        with self.assertNumQueries(2):
            person = Person.objects.prefetch_related('pets').get(name='Bella')
        with self.assertNumQueries(0):
            self.assertEqual(2, len(person.pets.all()))

    def test_prefetch_related_from_uuid_model_to_uuid_model(self):
        fleas = [Flea.objects.create() for i in range(3)]
        Pet.objects.create(name='Fifi').fleas_hosted.add(*fleas)
        Pet.objects.create(name='Bobo').fleas_hosted.add(*fleas)

        with self.assertNumQueries(2):
            pet = Pet.objects.prefetch_related('fleas_hosted').get(name='Fifi')
        with self.assertNumQueries(0):
            self.assertEqual(3, len(pet.fleas_hosted.all()))

        with self.assertNumQueries(2):
            flea = Flea.objects.prefetch_related('pets_visited').get(pk=fleas[0].pk)
        with self.assertNumQueries(0):
            self.assertEqual(2, len(flea.pets_visited.all()))

    def test_prefetch_related_from_uuid_model_to_uuid_model_with_values_flat(self):
        """
        Tests prefetching related objects from a UUID model to another UUID model using values_list with flat=True.
        
        This test verifies that the prefetch_related method correctly fetches related objects from a 'Pet' model to 'Person' model and returns the expected results using values_list with the flat=True parameter.
        
        Key Parameters:
        - None
        
        Keywords:
        - prefetch_related
        - UUID model
        - values_list
        - flat=True
        
        Input:
        - None
        
        Output:
        - A list containing the ID of the 'Pet'
        """

        pet = Pet.objects.create(name='Fifi')
        pet.people.add(
            Person.objects.create(name='Ellen'),
            Person.objects.create(name='George'),
        )
        self.assertSequenceEqual(
            Pet.objects.prefetch_related('fleas_hosted').values_list('id', flat=True),
            [pet.id]
        )


class UUIDPrefetchRelatedLookups(TestCase):

    @classmethod
    def setUpTestData(cls):
        house = House.objects.create(name='Redwood', address='Arcata')
        room = Room.objects.create(name='Racoon', house=house)
        fleas = [Flea.objects.create(current_room=room) for i in range(3)]
        pet = Pet.objects.create(name='Spooky')
        pet.fleas_hosted.add(*fleas)
        person = Person.objects.create(name='Bob')
        person.houses.add(house)
        person.pets.add(pet)
        person.fleas_hosted.add(*fleas)

    def test_from_uuid_pk_lookup_uuid_pk_integer_pk(self):
        # From uuid-pk model, prefetch <uuid-pk model>.<integer-pk model>:
        with self.assertNumQueries(4):
            spooky = Pet.objects.prefetch_related('fleas_hosted__current_room__house').get(name='Spooky')
        with self.assertNumQueries(0):
            self.assertEqual('Racoon', spooky.fleas_hosted.all()[0].current_room.name)

    def test_from_uuid_pk_lookup_integer_pk2_uuid_pk2(self):
        """
        Tests the prefetch functionality for a nested model lookup from a UUID primary key to an integer primary key and back to a UUID primary key.
        
        This test ensures that when querying a `Pet` object with the name 'Spooky' and prefetching related objects from a nested structure (Pet -> People -> Houses -> Rooms -> Fleas), the correct number of related `Flea` objects is retrieved.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - No external input is required for
        """

        # From uuid-pk model, prefetch <integer-pk model>.<integer-pk model>.<uuid-pk model>.<uuid-pk model>:
        with self.assertNumQueries(5):
            spooky = Pet.objects.prefetch_related('people__houses__rooms__fleas').get(name='Spooky')
        with self.assertNumQueries(0):
            self.assertEqual(3, len(spooky.people.all()[0].houses.all()[0].rooms.all()[0].fleas.all()))

    def test_from_integer_pk_lookup_uuid_pk_integer_pk(self):
        # From integer-pk model, prefetch <uuid-pk model>.<integer-pk model>:
        with self.assertNumQueries(3):
            racoon = Room.objects.prefetch_related('fleas__people_visited').get(name='Racoon')
        with self.assertNumQueries(0):
            self.assertEqual('Bob', racoon.fleas.all()[0].people_visited.all()[0].name)

    def test_from_integer_pk_lookup_integer_pk_uuid_pk(self):
        """
        Tests the behavior of prefetching related models with different primary keys (integer and UUID).
        
        This function performs a database query to retrieve a 'House' object with the name 'Redwood' and prefetch its related 'rooms' and 'fleas'. The 'rooms' are UUID-pk models and 'fleas' are related to them. The function asserts that the number of queries made is as expected and that the related 'fleas' can be accessed without additional queries.
        
        Parameters:
        """

        # From integer-pk model, prefetch <integer-pk model>.<uuid-pk model>:
        with self.assertNumQueries(3):
            redwood = House.objects.prefetch_related('rooms__fleas').get(name='Redwood')
        with self.assertNumQueries(0):
            self.assertEqual(3, len(redwood.rooms.all()[0].fleas.all()))

    def test_from_integer_pk_lookup_integer_pk_uuid_pk_uuid_pk(self):
        # From integer-pk model, prefetch <integer-pk model>.<uuid-pk model>.<uuid-pk model>:
        with self.assertNumQueries(4):
            redwood = House.objects.prefetch_related('rooms__fleas__pets_visited').get(name='Redwood')
        with self.assertNumQueries(0):
            self.assertEqual('Spooky', redwood.rooms.all()[0].fleas.all()[0].pets_visited.all()[0].name)
