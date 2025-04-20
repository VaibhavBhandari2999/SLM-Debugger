import os

from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from django.test.utils import extend_sys_path

from .models import (
    ConcreteModel,
    ConcreteModelSubclass,
    ConcreteModelSubclassProxy,
    ProxyModel,
)


class ProxyModelInheritanceTests(TransactionTestCase):
    """
    Proxy model inheritance across apps can result in migrate not creating the table
    for the proxied model (as described in #12286).  This test creates two dummy
    apps and calls migrate, then verifies that the table has been created.
    """

    available_apps = []

    def test_table_exists(self):
        """
        Tests the existence of database tables for specified models.
        
        This function sets up the necessary environment to test the existence of database tables for models defined in the 'app1' and 'app2' applications. It appends these applications to the INSTALLED_APPS setting, runs the migration commands to create the necessary tables, and then checks if the tables for the specified models exist.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Temporarily extend the system path to include the directory containing
        """

        with extend_sys_path(os.path.dirname(os.path.abspath(__file__))):
            with self.modify_settings(INSTALLED_APPS={"append": ["app1", "app2"]}):
                call_command("migrate", verbosity=0, run_syncdb=True)
                from app1.models import ProxyModel
                from app2.models import NiceModel

                self.assertEqual(NiceModel.objects.all().count(), 0)
                self.assertEqual(ProxyModel.objects.all().count(), 0)


class MultiTableInheritanceProxyTest(TestCase):
    def test_model_subclass_proxy(self):
        """
        Deleting an instance of a model proxying a multi-table inherited
        subclass should cascade delete down the whole inheritance chain (see
        #18083).
        """
        instance = ConcreteModelSubclassProxy.objects.create()
        instance.delete()
        self.assertEqual(0, ConcreteModelSubclassProxy.objects.count())
        self.assertEqual(0, ConcreteModelSubclass.objects.count())
        self.assertEqual(0, ConcreteModel.objects.count())

    def test_deletion_through_intermediate_proxy(self):
        """
        Tests the deletion of an instance through an intermediate proxy model.
        
        This function creates an instance of `ConcreteModelSubclass` and retrieves it via a `ProxyModel`. It then deletes the instance through the proxy model. The function asserts that after the deletion, no instances of either `ConcreteModel` or `ConcreteModelSubclass` exist in the database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates an instance of `ConcreteModelSubclass`.
        - Retrieves the created instance
        """

        child = ConcreteModelSubclass.objects.create()
        proxy = ProxyModel.objects.get(pk=child.pk)
        proxy.delete()
        self.assertFalse(ConcreteModel.objects.exists())
        self.assertFalse(ConcreteModelSubclass.objects.exists())
