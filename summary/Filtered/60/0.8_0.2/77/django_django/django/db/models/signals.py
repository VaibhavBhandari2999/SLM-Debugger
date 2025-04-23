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
        
        This function is designed to execute a method on a receiver object in a lazy manner, meaning the method is not immediately called but is scheduled for execution at a later time. It is particularly useful for operations that need to be deferred until the model is fully loaded.
        
        Parameters:
        method (callable): The method to be executed on the receiver object.
        apps (list): A list of Django apps to be used for lazy operations.
        receiver (object): The object
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
        """
        Connects a receiver function to a signal.
        
        This method connects a receiver function to a signal. The receiver function will be called when the signal is sent. The receiver can be a callable or a string that refers to a callable.
        
        Parameters:
        receiver (callable or str): The receiver function to connect to the signal.
        sender (type, optional): The sender of the signal. If not provided, the receiver will be connected to all senders. Default is None.
        weak (bool,
        """

        self._lazy_method(
            super().connect, apps, receiver, sender,
            weak=weak, dispatch_uid=dispatch_uid,
        )

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None, apps=None):
        """
        Disconnects signal receivers from the specified sender.
        
        This method is a lazy wrapper around the Django signal dispatcher's `disconnect` method.
        
        Parameters:
        receiver (object, optional): The receiver function or class to disconnect. If not provided, all receivers will be disconnected.
        sender (object, optional): The sender object that sent the signal. If not provided, all senders will be disconnected.
        dispatch_uid (str, optional): A unique identifier for the connection to be disconnected. If not provided
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
