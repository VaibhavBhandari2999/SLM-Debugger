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
        Lazy method execution for model operations.
        
        This function is designed to execute a specified method on a model in a lazy manner, meaning the operation is deferred until the model is accessed. It supports both string and model class inputs for the `sender` parameter.
        
        Parameters:
        method (callable): The method to be executed on the model.
        apps (list): A list of Django apps to consider for lazy operations. Defaults to None.
        receiver (object): The object that will receive the method call.
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
        Disconnects signal handlers from the specified receiver, sender, or dispatch_uid.
        
        Parameters:
        receiver (object, optional): The receiver to disconnect. If not provided, all receivers will be disconnected.
        sender (object, optional): The sender to disconnect. If not provided, all senders will be disconnected.
        dispatch_uid (str, optional): The unique identifier for the signal handler to disconnect.
        apps (list, optional): A list of Django apps to consider when disconnecting signals. If
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
