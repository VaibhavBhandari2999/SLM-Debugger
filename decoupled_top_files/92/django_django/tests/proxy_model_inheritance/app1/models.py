"""
This Python file contains a Django model proxy class named `ProxyModel`. It inherits from an existing model `NiceModel` defined in the `app2.models` module. The `Meta` class within `ProxyModel` sets the `proxy` attribute to `True`, indicating that `ProxyModel` does not create a new database table but rather provides a way to extend the functionality of `NiceModel` without altering its database schema. ```python
"""
from app2.models import NiceModel


class ProxyModel(NiceModel):
    class Meta:
        proxy = True
