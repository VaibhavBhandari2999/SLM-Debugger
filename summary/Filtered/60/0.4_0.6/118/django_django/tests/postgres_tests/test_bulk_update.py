from datetime import date

from . import PostgreSQLTestCase
from .models import (
    HStoreModel,
    IntegerArrayModel,
    NestedIntegerArrayModel,
    NullableIntegerArrayModel,
    OtherTypesArrayModel,
    RangesModel,
)

try:
    from django.db.backends.postgresql.psycopg_any import DateRange, NumericRange
except ImportError:
    pass  # psycopg isn't installed.


class BulkSaveTests(PostgreSQLTestCase):
    def test_bulk_update(self):
        """
        Tests the bulk update functionality for various models and fields.
        
        This function tests the bulk update method for different models and fields, ensuring that the updates are applied correctly. The function iterates through a list of test cases, where each case includes a model, a field name, initial data, and new data to be set.
        
        Parameters:
        - Model (class): The model class to be tested.
        - field (str): The field name on the model to be updated.
        - initial (list, int,
        """

        test_data = [
            (IntegerArrayModel, "field", [], [1, 2, 3]),
            (NullableIntegerArrayModel, "field", [1, 2, 3], None),
            (NestedIntegerArrayModel, "field", [], [[1, 2, 3]]),
            (HStoreModel, "field", {}, {1: 2}),
            (RangesModel, "ints", None, NumericRange(lower=1, upper=10)),
            (
                RangesModel,
                "dates",
                None,
                DateRange(lower=date.today(), upper=date.today()),
            ),
            (OtherTypesArrayModel, "ips", [], ["1.2.3.4"]),
            (OtherTypesArrayModel, "json", [], [{"a": "b"}]),
        ]
        for Model, field, initial, new in test_data:
            with self.subTest(model=Model, field=field):
                instances = Model.objects.bulk_create(
                    Model(**{field: initial}) for _ in range(20)
                )
                for instance in instances:
                    setattr(instance, field, new)
                Model.objects.bulk_update(instances, [field])
                self.assertSequenceEqual(
                    Model.objects.filter(**{field: new}), instances
                )
