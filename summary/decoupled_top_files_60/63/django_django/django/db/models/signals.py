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
        
        This function is designed to execute a specified method on a receiver object in a lazy manner, meaning the method is not immediately called but is scheduled for execution when the appropriate conditions are met.
        
        Parameters:
        method (callable): The method to be executed on the receiver object.
        apps (list): A list of Django apps to be used for lazy operations. If not provided, the default apps are used.
        receiver (object): The object on which the method will
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
        
        This method connects a receiver function to a signal. The receiver function will be called when the signal is sent.
        
        Parameters:
        receiver (function): The function to be connected as the receiver.
        sender (type or function, optional): The sender of the signal. If not specified, the receiver will be connected to all senders. Defaults to None.
        weak (bool, optional): Whether to use a weak reference to the receiver. If True,
        """

        self._lazy_method(
            super().connect, apps, receiver, sender,
            weak=weak, dispatch_uid=dispatch_uid,
        )

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None, apps=None):
        """
        Disconnects receivers from signals.
        
        This method disconnects receivers from signals. It accepts the following parameters:
        - `receiver`: The receiver function or class to disconnect. If `None`, all receivers will be disconnected.
        - `sender`: The sender model to disconnect. If `None`, all senders will be disconnected.
        - `dispatch_uid`: A unique identifier to specify which connection to disconnect. If `None`, all matching connections will be disconnected.
        - `apps`: The Django apps to use for resolving
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
