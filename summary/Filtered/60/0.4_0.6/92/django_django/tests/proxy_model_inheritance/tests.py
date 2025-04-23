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
        Tests the existence of database tables for specified models after running migrations.
        
        This function performs the following steps:
        1. Extends the system path to include the directory of the current file.
        2. Modifies the settings to append 'app1' and 'app2' to the INSTALLED_APPS list.
        3. Runs migrations with verbosity set to 0 and syncdb enabled.
        4. Imports the 'ProxyModel' from 'app1.models' and 'NiceModel' from 'app2.models'.
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
        child = ConcreteModelSubclass.objects.create()
        proxy = ProxyModel.objects.get(pk=child.pk)
        proxy.delete()
        self.assertFalse(ConcreteModel.objects.exists())
        self.assertFalse(ConcreteModelSubclass.objects.exists())
