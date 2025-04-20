import uuid
from datetime import datetime
from time import sleep

from django.contrib.postgres.functions import RandomUUID, TransactionNow

from . import PostgreSQLTestCase
from .models import NowTestModel, UUIDTestModel


class TestTransactionNow(PostgreSQLTestCase):
    def test_transaction_now(self):
        """
        The test case puts everything under a transaction, so two models
        updated with a short gap should have the same time.
        """
        m1 = NowTestModel.objects.create()
        m2 = NowTestModel.objects.create()

        NowTestModel.objects.filter(id=m1.id).update(when=TransactionNow())
        sleep(0.1)
        NowTestModel.objects.filter(id=m2.id).update(when=TransactionNow())

        m1.refresh_from_db()
        m2.refresh_from_db()

        self.assertIsInstance(m1.when, datetime)
        self.assertEqual(m1.when, m2.when)


class TestRandomUUID(PostgreSQLTestCase):
    def test_random_uuid(self):
        """
        Tests the creation and updating of UUIDs for UUIDTestModel instances.
        
        This function creates two instances of UUIDTestModel, checks that their UUIDs are valid UUIDs, and ensures that the UUIDs are different. It then updates the UUIDs of both instances to new random UUIDs and verifies that the updated UUIDs are still valid and unique.
        
        Key Parameters:
        - None (the function uses internal model instances)
        
        Keywords:
        - None
        
        Input:
        - None (the function uses internal model instances and
        """

        m1 = UUIDTestModel.objects.create()
        m2 = UUIDTestModel.objects.create()
        UUIDTestModel.objects.update(uuid=RandomUUID())
        m1.refresh_from_db()
        m2.refresh_from_db()
        self.assertIsInstance(m1.uuid, uuid.UUID)
        self.assertNotEqual(m1.uuid, m2.uuid)
