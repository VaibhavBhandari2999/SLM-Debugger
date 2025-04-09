from math import ceil

from django.db import IntegrityError, connection, models
from django.db.models.sql.constants import GET_ITERATOR_CHUNK_SIZE
from django.test import TestCase, skipIfDBFeature, skipUnlessDBFeature

from .models import (
    MR, A, Avatar, Base, Child, HiddenUser, HiddenUserProfile, M, M2MFrom,
    M2MTo, MRNull, Parent, R, RChild, S, T, User, create_a, get_default_r,
)


class OnDeleteTests(TestCase):
    def setUp(self):
        self.DEFAULT = get_default_r()

    def test_auto(self):
        """
        Tests the deletion of an 'auto' object created using the `create_a` function. Creates an 'auto' object, deletes it, and verifies its absence in the database using `A.objects.filter(name='auto').exists()`.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an 'auto' object.
        - `delete`: Deletes the created 'auto' object.
        - `A.objects.filter(name='auto').exists
        """

        a = create_a('auto')
        a.auto.delete()
        self.assertFalse(A.objects.filter(name='auto').exists())

    def test_auto_nullable(self):
        """
        Tests the behavior of the 'auto_nullable' field. Deletes the associated object and verifies that the object no longer exists in the database.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an instance of the 'auto_nullable' model.
        - `a.auto_nullable.delete()`: Deletes the 'auto_nullable' field of the created instance.
        - `A.objects.filter(name='auto_nullable').exists()`: Checks if any objects with
        """

        a = create_a('auto_nullable')
        a.auto_nullable.delete()
        self.assertFalse(A.objects.filter(name='auto_nullable').exists())

    def test_setvalue(self):
        """
        Tests the setvalue method by deleting the associated object and retrieving the default value.
        
        This function creates an instance of 'A' with the name 'setvalue', deletes the setvalue object, and then retrieves the instance again to check if the default value is restored.
        """

        a = create_a('setvalue')
        a.setvalue.delete()
        a = A.objects.get(pk=a.pk)
        self.assertEqual(self.DEFAULT, a.setvalue.pk)

    def test_setnull(self):
        """
        Tests the functionality of setting a related field to null using the `setnull` method.
        
        This function creates an instance of model 'A' with the name 'setnull', sets its related field `setnull` to null, and then retrieves the instance again to verify that the related field is indeed null.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an instance of model 'A'.
        - `a.setnull
        """

        a = create_a('setnull')
        a.setnull.delete()
        a = A.objects.get(pk=a.pk)
        self.assertIsNone(a.setnull)

    def test_setdefault(self):
        """
        Tests the 'setdefault' method of the 'A' model. Deletes the existing 'setdefault' object associated with an instance of 'A', retrieves the updated instance from the database, and asserts that the 'pk' of the 'setdefault' field is equal to the default value specified in the test.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an instance of the 'A' model.
        - `a.setdefault
        """

        a = create_a('setdefault')
        a.setdefault.delete()
        a = A.objects.get(pk=a.pk)
        self.assertEqual(self.DEFAULT, a.setdefault.pk)

    def test_setdefault_none(self):
        """
        Tests the `setdefault_none` method of the `A` model. Deletes the related object, retrieves the instance again, and checks if the `setdefault_none` field is set to None.
        """

        a = create_a('setdefault_none')
        a.setdefault_none.delete()
        a = A.objects.get(pk=a.pk)
        self.assertIsNone(a.setdefault_none)

    def test_cascade(self):
        """
        Tests the deletion of an object created with the 'cascade' method. Deletes the object 'a' and verifies that no objects with the name 'cascade' exist in the database.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an object with the specified name.
        - `delete`: Deletes the object.
        - `A.objects.filter(name='cascade').exists()`: Checks if any objects with the name 'cascade' exist in
        """

        a = create_a('cascade')
        a.cascade.delete()
        self.assertFalse(A.objects.filter(name='cascade').exists())

    def test_cascade_nullable(self):
        """
        Tests the cascade delete functionality for nullable fields.
        
        This function creates an instance of model 'A' with name 'cascade_nullable', deletes the instance, and checks if the object is removed from the database.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an instance of model 'A'.
        - `delete`: Deletes the created instance.
        - `filter`: Filters the objects in the database.
        - `exists`: Checks if
        """

        a = create_a('cascade_nullable')
        a.cascade_nullable.delete()
        self.assertFalse(A.objects.filter(name='cascade_nullable').exists())

    def test_protect(self):
        """
        Test protecting an instance of model 'A' that has a protected foreign key relationship with model 'R'. Attempting to delete the protected instance raises an IntegrityError with a specific message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        IntegrityError: If the protected instance is deleted, an IntegrityError is raised with the message: "Cannot delete some instances of model 'R' because they are referenced through a protected foreign key: 'A.protect'"
        
        Functions
        """

        a = create_a('protect')
        msg = (
            "Cannot delete some instances of model 'R' because they are "
            "referenced through a protected foreign key: 'A.protect'"
        )
        with self.assertRaisesMessage(IntegrityError, msg):
            a.protect.delete()

    def test_do_nothing(self):
        """
        Tests the 'DO_NOTHING' behavior for foreign key deletion. Connects to the pre_delete signal to replace the deleted object with a known replacement object. Deletes an instance of A that has a related DoNothing object, then verifies that the DoNothing object was replaced with the specified replacement object.
        
        Functions Used:
        - `R.objects.create()`: Creates a new instance of the `R` model.
        - `models.signals.pre_delete.connect(check_do_nothing)`: Connects the `
        """

        # Testing DO_NOTHING is a bit harder: It would raise IntegrityError for a normal model,
        # so we connect to pre_delete and set the fk to a known value.
        replacement_r = R.objects.create()

        def check_do_nothing(sender, **kwargs):
            obj = kwargs['instance']
            obj.donothing_set.update(donothing=replacement_r)
        models.signals.pre_delete.connect(check_do_nothing)
        a = create_a('do_nothing')
        a.donothing.delete()
        a = A.objects.get(pk=a.pk)
        self.assertEqual(replacement_r, a.donothing)
        models.signals.pre_delete.disconnect(check_do_nothing)

    def test_do_nothing_qscount(self):
        """
        A models.DO_NOTHING relation doesn't trigger a query.
        """
        b = Base.objects.create()
        with self.assertNumQueries(1):
            # RelToBase should not be queried.
            b.delete()
        self.assertEqual(Base.objects.count(), 0)

    def test_inheritance_cascade_up(self):
        """
        Tests inheritance cascade delete upwards from a child model (RChild) to its parent models (R and L).
        
        Args:
        None
        
        Returns:
        None
        
        Methods:
        - RChild.objects.create(): Creates an instance of the RChild model.
        - child.delete(): Deletes the created RChild instance.
        - R.objects.filter(pk=child.pk).exists(): Checks if the parent model (R) still exists after the deletion.
        
        Important Notes:
        - The function verifies
        """

        child = RChild.objects.create()
        child.delete()
        self.assertFalse(R.objects.filter(pk=child.pk).exists())

    def test_inheritance_cascade_down(self):
        """
        Tests inheritance cascade down behavior.
        
        This function creates an instance of `RChild`, deletes its parent (`RChild`'s `r_ptr`), and checks if the `RChild` instance still exists in the database.
        
        :param None: No parameters are passed directly to this function.
        :return: None
        """

        child = RChild.objects.create()
        parent = child.r_ptr
        parent.delete()
        self.assertFalse(RChild.objects.filter(pk=child.pk).exists())

    def test_cascade_from_child(self):
        """
        Tests the cascade deletion from a child object. Deletes the child of an 'A' object and verifies that both the 'A' object's child reference and the related 'R' object are no longer present in the database.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an 'A' object with a specified name.
        - `delete`: Deletes the child object associated with an 'A' object.
        - `filter`:
        """

        a = create_a('child')
        a.child.delete()
        self.assertFalse(A.objects.filter(name='child').exists())
        self.assertFalse(R.objects.filter(pk=a.child_id).exists())

    def test_cascade_from_parent(self):
        """
        Tests cascading deletion from parent model.
        
        This function creates an instance of `A` with the name 'child', then deletes
        its related instance in the `R` model using `get` and `delete`. It checks
        that both the parent (`A`) and child (`RChild`) instances no longer exist in
        the database.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - :func:`create_a`
        - :func
        """

        a = create_a('child')
        R.objects.get(pk=a.child_id).delete()
        self.assertFalse(A.objects.filter(name='child').exists())
        self.assertFalse(RChild.objects.filter(pk=a.child_id).exists())

    def test_setnull_from_child(self):
        """
        Tests setting a child object to null using `setnull` on a ForeignKey relationship.
        
        This function creates an instance of model 'A' with a related child object, deletes the child object,
        and then verifies that the ForeignKey field in the parent object is set to None.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `create_a`: Creates an instance of model 'A' with a related child object.
        - `delete`: Deletes the child
        """

        a = create_a('child_setnull')
        a.child_setnull.delete()
        self.assertFalse(R.objects.filter(pk=a.child_setnull_id).exists())

        a = A.objects.get(pk=a.pk)
        self.assertIsNone(a.child_setnull)

    def test_setnull_from_parent(self):
        """
        Tests setting a child object to null in the parent model after deleting the child.
        
        This function creates an instance of `A` with a related `RChild` object, deletes the `RChild`, and then verifies that the `child_setnull` field in the parent model is set to None.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an instance of `A` with a related `RChild`.
        - `
        """

        a = create_a('child_setnull')
        R.objects.get(pk=a.child_setnull_id).delete()
        self.assertFalse(RChild.objects.filter(pk=a.child_setnull_id).exists())

        a = A.objects.get(pk=a.pk)
        self.assertIsNone(a.child_setnull)

    def test_o2o_setnull(self):
        """
        Tests the behavior of setting a one-to-one relationship field to null.
        
        This function creates an instance of model 'A' with the name 'o2o_setnull', deletes the related object, and retrieves the instance again. It then checks if the one-to-one relationship field is set to None.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `create_a`: Creates an instance of model 'A'.
        - `delete()`: Deletes the related
        """

        a = create_a('o2o_setnull')
        a.o2o_setnull.delete()
        a = A.objects.get(pk=a.pk)
        self.assertIsNone(a.o2o_setnull)


class DeletionTests(TestCase):

    def test_m2m(self):
        """
        Tests the behavior of Many-to-Many relationships with custom through models and deletion.
        
        This function verifies that when related objects are deleted, the corresponding entries in the custom through model are also deleted. It covers scenarios where:
        - A related object is deleted directly.
        - The main object is deleted.
        - A related object is added using the custom through model and then deleted.
        - A related object is added using the custom through model and then the main object is deleted.
        - A
        """

        m = M.objects.create()
        r = R.objects.create()
        MR.objects.create(m=m, r=r)
        r.delete()
        self.assertFalse(MR.objects.exists())

        r = R.objects.create()
        MR.objects.create(m=m, r=r)
        m.delete()
        self.assertFalse(MR.objects.exists())

        m = M.objects.create()
        r = R.objects.create()
        m.m2m.add(r)
        r.delete()
        through = M._meta.get_field('m2m').remote_field.through
        self.assertFalse(through.objects.exists())

        r = R.objects.create()
        m.m2m.add(r)
        m.delete()
        self.assertFalse(through.objects.exists())

        m = M.objects.create()
        r = R.objects.create()
        MRNull.objects.create(m=m, r=r)
        r.delete()
        self.assertFalse(not MRNull.objects.exists())
        self.assertFalse(m.m2m_through_null.exists())

    def test_bulk(self):
        """
        Tests bulk deletion of related objects.
        
        This function creates an instance of `S` with a related instance of `R`,
        then creates multiple instances of `T` related to `S`. It measures the number
        of queries executed when deleting the `S` instance and its related objects.
        
        :param None: No parameters are required for this function.
        :return: None
        """

        s = S.objects.create(r=R.objects.create())
        for i in range(2 * GET_ITERATOR_CHUNK_SIZE):
            T.objects.create(s=s)
        #   1 (select related `T` instances)
        # + 1 (select related `U` instances)
        # + 2 (delete `T` instances in batches)
        # + 1 (delete `s`)
        self.assertNumQueries(5, s.delete)
        self.assertFalse(S.objects.exists())

    def test_instance_update(self):
        """
        Connects a pre-delete signal to track instance deletions and related setnull sets. Deletes instances of A with specific names ('update_setnull' and 'update_cascade'), then verifies that the deleted instances and their related setnull objects are properly handled.
        
        Summary:
        - Connects: `models.signals.pre_delete`
        - Triggers: `pre_delete` function
        - Deletes: Instances of A with names 'update_setnull' and 'update_cascade'
        - Verifies
        """

        deleted = []
        related_setnull_sets = []

        def pre_delete(sender, **kwargs):
            """
            Pre-delete signal handler for models.
            
            This function is triggered before an instance of a model is deleted. It appends
            the instance to the `deleted` list and checks if the instance is an instance of
            `R`. If it is, it collects the primary keys of all related instances from the
            `setnull_set` and appends them to the `related_setnull_sets` list.
            
            Args:
            sender (Model): The model class that is being deleted.
            """

            obj = kwargs['instance']
            deleted.append(obj)
            if isinstance(obj, R):
                related_setnull_sets.append([a.pk for a in obj.setnull_set.all()])

        models.signals.pre_delete.connect(pre_delete)
        a = create_a('update_setnull')
        a.setnull.delete()

        a = create_a('update_cascade')
        a.cascade.delete()

        for obj in deleted:
            self.assertIsNone(obj.pk)

        for pk_list in related_setnull_sets:
            for a in A.objects.filter(id__in=pk_list):
                self.assertIsNone(a.setnull)

        models.signals.pre_delete.disconnect(pre_delete)

    def test_deletion_order(self):
        """
        Tests the order of deletion signals for related objects.
        
        This function connects to the `post_delete` and `pre_delete` signals to
        log the order in which related objects are deleted. It creates instances
        of `R`, `S`, `T`, and `RChild` models, then deletes an instance of `R`.
        The expected order of pre-delete and post-delete signal logs is verified
        using assertions.
        
        Important Functions:
        - `models.signals.post_delete.connect
        """

        pre_delete_order = []
        post_delete_order = []

        def log_post_delete(sender, **kwargs):
            """
            Logs the deletion of a specific instance.
            
            This function is triggered when an instance of model 'S' is deleted. It checks if the related object with the given 'r_id' exists in the R model using R.objects.filter(). If the related object exists, it appends the ID of the deleted instance to the 'deletions' list.
            
            Args:
            instance (S): The instance of model 'S' that is being deleted.
            
            Returns:
            None
            """

            pre_delete_order.append((sender, kwargs['instance'].pk))

        def log_pre_delete(sender, **kwargs):
            post_delete_order.append((sender, kwargs['instance'].pk))

        models.signals.post_delete.connect(log_post_delete)
        models.signals.pre_delete.connect(log_pre_delete)

        r = R.objects.create(pk=1)
        s1 = S.objects.create(pk=1, r=r)
        s2 = S.objects.create(pk=2, r=r)
        T.objects.create(pk=1, s=s1)
        T.objects.create(pk=2, s=s2)
        RChild.objects.create(r_ptr=r)
        r.delete()
        self.assertEqual(
            pre_delete_order, [(T, 2), (T, 1), (RChild, 1), (S, 2), (S, 1), (R, 1)]
        )
        self.assertEqual(
            post_delete_order, [(T, 1), (T, 2), (RChild, 1), (S, 1), (S, 2), (R, 1)]
        )

        models.signals.post_delete.disconnect(log_post_delete)
        models.signals.pre_delete.disconnect(log_pre_delete)

    def test_relational_post_delete_signals_happen_before_parent_object(self):
        """
        Tests that post-delete signals for relational objects are triggered before the parent object is deleted.
        
        This function connects a post-delete signal handler to the `S` model, which logs the deletion of related instances of `S`. It creates an instance of `R` and a related instance of `S`, then deletes the `R` instance. The signal handler ensures that the related `S` instance is deleted after the `R` instance but before the parent object's deletion is finalized.
        
        :param
        """

        deletions = []

        def log_post_delete(instance, **kwargs):
            self.assertTrue(R.objects.filter(pk=instance.r_id))
            self.assertIs(type(instance), S)
            deletions.append(instance.id)

        r = R.objects.create(pk=1)
        S.objects.create(pk=1, r=r)

        models.signals.post_delete.connect(log_post_delete, sender=S)

        try:
            r.delete()
        finally:
            models.signals.post_delete.disconnect(log_post_delete)

        self.assertEqual(len(deletions), 1)
        self.assertEqual(deletions[0], 1)

    @skipUnlessDBFeature("can_defer_constraint_checks")
    def test_can_defer_constraint_checks(self):
        """
        Tests the ability to defer constraint checks during deletion of an Avatar object.
        
        This function creates a User and an associated Avatar, then deletes the Avatar.
        It ensures that no UPDATE operation is performed on the User's avatar field
        when constraint checks are deferred. The function uses signals to prevent
        fast deletions and measures the number of database queries executed during
        the deletion process.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `
        """

        u = User.objects.create(
            avatar=Avatar.objects.create()
        )
        a = Avatar.objects.get(pk=u.avatar_id)
        # 1 query to find the users for the avatar.
        # 1 query to delete the user
        # 1 query to delete the avatar
        # The important thing is that when we can defer constraint checks there
        # is no need to do an UPDATE on User.avatar to null it out.

        # Attach a signal to make sure we will not do fast_deletes.
        calls = []

        def noop(*args, **kwargs):
            calls.append('')
        models.signals.post_delete.connect(noop, sender=User)

        self.assertNumQueries(3, a.delete)
        self.assertFalse(User.objects.exists())
        self.assertFalse(Avatar.objects.exists())
        self.assertEqual(len(calls), 1)
        models.signals.post_delete.disconnect(noop, sender=User)

    @skipIfDBFeature("can_defer_constraint_checks")
    def test_cannot_defer_constraint_checks(self):
        """
        Tests that constraints cannot be deferred when deleting a model instance.
        
        This function creates a `User` instance with an associated `Avatar` object.
        It then attaches a post-delete signal to prevent fast deletions and deletes
        the `Avatar` object. The function asserts that four queries are executed
        during the deletion process: one to find the users for the avatar, one to
        delete the user, one to null out the user's avatar field, and one to delete
        """

        u = User.objects.create(
            avatar=Avatar.objects.create()
        )
        # Attach a signal to make sure we will not do fast_deletes.
        calls = []

        def noop(*args, **kwargs):
            calls.append('')
        models.signals.post_delete.connect(noop, sender=User)

        a = Avatar.objects.get(pk=u.avatar_id)
        # The below doesn't make sense... Why do we need to null out
        # user.avatar if we are going to delete the user immediately after it,
        # and there are no more cascades.
        # 1 query to find the users for the avatar.
        # 1 query to delete the user
        # 1 query to null out user.avatar, because we can't defer the constraint
        # 1 query to delete the avatar
        self.assertNumQueries(4, a.delete)
        self.assertFalse(User.objects.exists())
        self.assertFalse(Avatar.objects.exists())
        self.assertEqual(len(calls), 1)
        models.signals.post_delete.disconnect(noop, sender=User)

    def test_hidden_related(self):
        """
        Tests the deletion of a related object in the `HiddenUserProfile` model.
        
        This function creates an instance of `R`, then creates a corresponding `HiddenUser` and `HiddenUserProfile`. It deletes the `R` object and checks if the `HiddenUserProfile` is also deleted.
        
        - `R`: The related object being created and deleted.
        - `HiddenUser`: The hidden user object associated with `R`.
        - `HiddenUserProfile`: The profile object associated with the hidden user.
        """

        r = R.objects.create()
        h = HiddenUser.objects.create(r=r)
        HiddenUserProfile.objects.create(user=h)

        r.delete()
        self.assertEqual(HiddenUserProfile.objects.count(), 0)

    def test_large_delete(self):
        """
        Tests the deletion of a large number of Avatar objects.
        
        This function creates a large number of Avatar objects using `bulk_create` and then deletes them in batches. It calculates the number of database queries required based on the batch size and the total number of objects. The function asserts that the expected number of queries matches the actual number of queries performed during the deletion process. After the deletion, it verifies that no Avatar objects exist in the database.
        
        Args:
        None
        
        Returns:
        None
        """

        TEST_SIZE = 2000
        objs = [Avatar() for i in range(0, TEST_SIZE)]
        Avatar.objects.bulk_create(objs)
        # Calculate the number of queries needed.
        batch_size = connection.ops.bulk_batch_size(['pk'], objs)
        # The related fetches are done in batches.
        batches = ceil(len(objs) / batch_size)
        # One query for Avatar.objects.all() and then one related fast delete for
        # each batch.
        fetches_to_mem = 1 + batches
        # The Avatar objects are going to be deleted in batches of GET_ITERATOR_CHUNK_SIZE
        queries = fetches_to_mem + TEST_SIZE // GET_ITERATOR_CHUNK_SIZE
        self.assertNumQueries(queries, Avatar.objects.all().delete)
        self.assertFalse(Avatar.objects.exists())

    def test_large_delete_related(self):
        """
        Tests the deletion of a large number of related objects.
        
        This function creates a parent object `S` with a related object `R`, and then creates a large number of child objects `T` related to `S`. It measures the number of database queries performed when deleting all `T` objects in batches and finally deletes the parent object `S`.
        
        :param TEST_SIZE: The number of child objects `T` to create.
        :type TEST_SIZE: int
        :return:
        """

        TEST_SIZE = 2000
        s = S.objects.create(r=R.objects.create())
        for i in range(TEST_SIZE):
            T.objects.create(s=s)

        batch_size = max(connection.ops.bulk_batch_size(['pk'], range(TEST_SIZE)), 1)

        # TEST_SIZE / batch_size (select related `T` instances)
        # + 1 (select related `U` instances)
        # + TEST_SIZE / GET_ITERATOR_CHUNK_SIZE (delete `T` instances in batches)
        # + 1 (delete `s`)
        expected_num_queries = ceil(TEST_SIZE / batch_size)
        expected_num_queries += ceil(TEST_SIZE / GET_ITERATOR_CHUNK_SIZE) + 2

        self.assertNumQueries(expected_num_queries, s.delete)
        self.assertFalse(S.objects.exists())
        self.assertFalse(T.objects.exists())

    def test_delete_with_keeping_parents(self):
        """
        Delete a child record while keeping its parent.
        
        This function creates a new `RChild` instance, retrieves its parent's ID,
        deletes the child while keeping its parent, and then checks if the child
        and parent records still exist in the database.
        
        :param None: No parameters are passed directly to this function.
        :return: None
        
        - **Important Functions:** `create`, `delete(keep_parents=True)`, `filter`
        - **Affects Variables:**
        """

        child = RChild.objects.create()
        parent_id = child.r_ptr_id
        child.delete(keep_parents=True)
        self.assertFalse(RChild.objects.filter(id=child.id).exists())
        self.assertTrue(R.objects.filter(id=parent_id).exists())

    def test_delete_with_keeping_parents_relationships(self):
        """
        Delete a child object while keeping its parent relationships intact.
        
        This function creates an instance of `RChild`, establishes a relationship with `S` through `R`, and then deletes the `RChild` object while preserving the parent-child relationships. The function asserts that the `RChild` object is deleted, but its parent (`R`) and referent (`S`) remain intact.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `RChild.objects.create
        """

        child = RChild.objects.create()
        parent_id = child.r_ptr_id
        parent_referent_id = S.objects.create(r=child.r_ptr).pk
        child.delete(keep_parents=True)
        self.assertFalse(RChild.objects.filter(id=child.id).exists())
        self.assertTrue(R.objects.filter(id=parent_id).exists())
        self.assertTrue(S.objects.filter(pk=parent_referent_id).exists())

    def test_queryset_delete_returns_num_rows(self):
        """
        QuerySet.delete() should return the number of deleted rows and a
        dictionary with the number of deletions for each object type.
        """
        Avatar.objects.bulk_create([Avatar(desc='a'), Avatar(desc='b'), Avatar(desc='c')])
        avatars_count = Avatar.objects.count()
        deleted, rows_count = Avatar.objects.all().delete()
        self.assertEqual(deleted, avatars_count)

        # more complex example with multiple object types
        r = R.objects.create()
        h1 = HiddenUser.objects.create(r=r)
        HiddenUser.objects.create(r=r)
        HiddenUserProfile.objects.create(user=h1)
        existed_objs = {
            R._meta.label: R.objects.count(),
            HiddenUser._meta.label: HiddenUser.objects.count(),
            A._meta.label: A.objects.count(),
            MR._meta.label: MR.objects.count(),
            HiddenUserProfile._meta.label: HiddenUserProfile.objects.count(),
        }
        deleted, deleted_objs = R.objects.all().delete()
        for k, v in existed_objs.items():
            self.assertEqual(deleted_objs[k], v)

    def test_model_delete_returns_num_rows(self):
        """
        Model.delete() should return the number of deleted rows and a
        dictionary with the number of deletions for each object type.
        """
        r = R.objects.create()
        h1 = HiddenUser.objects.create(r=r)
        h2 = HiddenUser.objects.create(r=r)
        HiddenUser.objects.create(r=r)
        HiddenUserProfile.objects.create(user=h1)
        HiddenUserProfile.objects.create(user=h2)
        m1 = M.objects.create()
        m2 = M.objects.create()
        MR.objects.create(r=r, m=m1)
        r.m_set.add(m1)
        r.m_set.add(m2)
        r.save()
        existed_objs = {
            R._meta.label: R.objects.count(),
            HiddenUser._meta.label: HiddenUser.objects.count(),
            A._meta.label: A.objects.count(),
            MR._meta.label: MR.objects.count(),
            HiddenUserProfile._meta.label: HiddenUserProfile.objects.count(),
            M.m2m.through._meta.label: M.m2m.through.objects.count(),
        }
        deleted, deleted_objs = r.delete()
        self.assertEqual(deleted, sum(existed_objs.values()))
        for k, v in existed_objs.items():
            self.assertEqual(deleted_objs[k], v)

    def test_proxied_model_duplicate_queries(self):
        """
        #25685 - Deleting instances of a model with existing proxy
        classes should not issue multiple queries during cascade
        deletion of referring models.
        """
        avatar = Avatar.objects.create()
        # One query for the Avatar table and a second for the User one.
        with self.assertNumQueries(2):
            avatar.delete()


class FastDeleteTests(TestCase):

    def test_fast_delete_fk(self):
        """
        Tests the fast deletion of a ForeignKey relationship between a User and an Avatar model. Creates a User with an associated Avatar, then deletes the Avatar using `a.delete()`. Ensures that both the User and Avatar are deleted, resulting in no instances of either model existing in the database. Utilizes `assertNumQueries` to verify that only two queries are executed during the deletion process.
        """

        u = User.objects.create(
            avatar=Avatar.objects.create()
        )
        a = Avatar.objects.get(pk=u.avatar_id)
        # 1 query to fast-delete the user
        # 1 query to delete the avatar
        self.assertNumQueries(2, a.delete)
        self.assertFalse(User.objects.exists())
        self.assertFalse(Avatar.objects.exists())

    def test_fast_delete_m2m(self):
        """
        Tests the fast deletion of a Many-to-Many relationship.
        
        This function creates an instance of `M2MTo` and `M2MFrom`, adds the `M2MTo`
        instance to the `M2MFrom` instance's Many-to-Many field, and then measures
        the number of queries required to delete the `M2MFrom` instance using the
        `delete` method. It expects two queries: one for deleting the `M2M
        """

        t = M2MTo.objects.create()
        f = M2MFrom.objects.create()
        f.m2m.add(t)
        # 1 to delete f, 1 to fast-delete m2m for f
        self.assertNumQueries(2, f.delete)

    def test_fast_delete_revm2m(self):
        """
        Delete an instance of M2MFrom and its related M2MTo objects using fast deletion.
        
        This function creates an instance of M2MTo and M2MFrom, establishes a many-to-many relationship between them,
        and then deletes the M2MFrom instance using fast deletion. The number of queries executed during this process is
        expected to be two: one for deleting the M2MFrom instance and another for fast-deleting the related M2MTo objects.
        """

        t = M2MTo.objects.create()
        f = M2MFrom.objects.create()
        f.m2m.add(t)
        # 1 to delete t, 1 to fast-delete t's m_set
        self.assertNumQueries(2, f.delete)

    def test_fast_delete_qs(self):
        """
        Delete a specific user instance using QuerySet.delete and assert that only one query is executed. Verify that the remaining user instance still exists.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `User.objects.create()`: Creates new user instances.
        - `User.objects.filter(pk=u1.pk).delete()`: Deletes the specified user instance.
        - `self.assertNumQueries(1, ... )`: Asserts that only one database query is executed.
        """

        u1 = User.objects.create()
        u2 = User.objects.create()
        self.assertNumQueries(1, User.objects.filter(pk=u1.pk).delete)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(pk=u2.pk).exists())

    def test_fast_delete_joined_qs(self):
        """
        Delete users with associated avatars where avatar description is 'a'. This test asserts that the deletion operation generates the expected number of database queries, depending on the `update_can_self_select` feature of the database connection. It also verifies that only one user is left after the deletion and that a specific user (`u2`) is not deleted.
        
        :param None: No additional parameters are required for this test.
        :return None: The function does not return any value. It asserts conditions using `
        """

        a = Avatar.objects.create(desc='a')
        User.objects.create(avatar=a)
        u2 = User.objects.create()
        expected_queries = 1 if connection.features.update_can_self_select else 2
        self.assertNumQueries(expected_queries,
                              User.objects.filter(avatar__desc='a').delete)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(pk=u2.pk).exists())

    def test_fast_delete_inheritance(self):
        """
        Tests the fast deletion of an inheritance model.
        
        This function verifies that deleting instances of `Child` and `Parent` models
        works correctly, ensuring that related objects are properly deleted or left
        intact based on their relationships. It uses `assertNumQueries` to check the
        number of database queries executed during the deletion process. The function
        creates instances of both models, performs deletions, and asserts the expected
        state of the database after each operation.
        
        - `
        """

        c = Child.objects.create()
        p = Parent.objects.create()
        # 1 for self, 1 for parent
        self.assertNumQueries(2, c.delete)
        self.assertFalse(Child.objects.exists())
        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Parent.objects.filter(pk=p.pk).count(), 1)
        # 1 for self delete, 1 for fast delete of empty "child" qs.
        self.assertNumQueries(2, p.delete)
        self.assertFalse(Parent.objects.exists())
        # 1 for self delete, 1 for fast delete of empty "child" qs.
        c = Child.objects.create()
        p = c.parent_ptr
        self.assertNumQueries(2, p.delete)
        self.assertFalse(Parent.objects.exists())
        self.assertFalse(Child.objects.exists())

    def test_fast_delete_large_batch(self):
        """
        This function tests the deletion of large batches of users and their associated avatars. It creates 2000 user objects and 2000 avatar objects, then deletes them all efficiently using bulk operations. The function ensures that no parameter amount limits are exceeded during the deletion process and verifies that all users are successfully deleted.
        """

        User.objects.bulk_create(User() for i in range(0, 2000))
        # No problems here - we aren't going to cascade, so we will fast
        # delete the objects in a single query.
        self.assertNumQueries(1, User.objects.all().delete)
        a = Avatar.objects.create(desc='a')
        User.objects.bulk_create(User(avatar=a) for i in range(0, 2000))
        # We don't hit parameter amount limits for a, so just one query for
        # that + fast delete of the related objs.
        self.assertNumQueries(2, a.delete)
        self.assertEqual(User.objects.count(), 0)

    def test_fast_delete_empty_no_update_can_self_select(self):
        """
        #25932 - Fast deleting on backends that don't have the
        `no_update_can_self_select` feature should work even if the specified
        filter doesn't match any row.
        """
        with self.assertNumQueries(1):
            self.assertEqual(
                User.objects.filter(avatar__desc='missing').delete(),
                (0, {'delete.User': 0})
            )
