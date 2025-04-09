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
        Bulk update multiple instances of a model with new values for a specified field. This function tests the bulk update functionality for various models and fields.
        
        Args:
        None (The function uses predefined test data)
        
        Summary:
        - Models tested: IntegerArrayModel, NullableIntegerArrayModel, NestedIntegerArrayModel, HStoreModel, RangesModel, OtherTypesArrayModel
        - Fields updated: 'field', 'ints', 'dates', 'ips', 'json'
        - Functions used
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
