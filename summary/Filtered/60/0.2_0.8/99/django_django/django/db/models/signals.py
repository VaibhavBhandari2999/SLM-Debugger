from functools import partial

from django.db.models.utils import make_model_tuple
from django.dispatch import Signal

class_prepared = Signal()


class ModelSignal(Signal):
    """
    Signal subclass that allows the sender to be lazily specified as a string
    of the `app_label.ModelName` form.
    """

    def _lazy_method(self, method, apps, receiver, sender, **kwargs):
        """
        Lazy method execution for Django models.
        
        This function is designed to execute a method on a receiver object in a lazy manner, meaning the method is not immediately called but is scheduled for execution. It supports both model and application-level lazy operations.
        
        Parameters:
        method (callable): The method to be executed on the receiver object.
        apps (list): A list of Django apps to be used for lazy operations. If not provided, the default apps are used.
        receiver (object): The object on which
        """

        from django.db.models.options import Options

        # This partial takes a single optional argument named "sender".
        partial_method = partial(method, receiver, **kwargs)
        if isinstance(sender, str):
            apps = apps or Options.default_apps
            apps.lazy_model_operation(partial_method, make_model_tuple(sender))
        else:
            return partial_method(sender)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None, apps=None):
        self._lazy_method(
            super().connect,
            apps,
            receiver,
            sender,
            weak=weak,
            dispatch_uid=dispatch_uid,
        )

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None, apps=None):
        """
        Disconnects signal receivers from the dispatcher.
        
        This method disconnects signal receivers from the dispatcher. It accepts the following parameters:
        - `receiver`: The receiver function or class to disconnect. If `None`, all receivers are disconnected.
        - `sender`: The sender object to disconnect. If `None`, all senders are disconnected.
        - `dispatch_uid`: A unique identifier for the connection to be disconnected.
        - `apps`: An optional parameter for specifying the application registry.
        
        Returns:
        - None: This method
        """

        return self._lazy_method(
            super().disconnect, apps, receiver, sender, dispatch_uid=dispatch_uid
        )


pre_init = ModelSignal(use_caching=True)
post_init = ModelSignal(use_caching=True)

pre_save = ModelSignal(use_caching=True)
post_save = ModelSignal(use_caching=True)

pre_delete = ModelSignal(use_caching=True)
post_delete = ModelSignal(use_caching=True)

m2m_changed = ModelSignal(use_caching=True)

pre_migrate = Signal()
post_migrate = Signal()
