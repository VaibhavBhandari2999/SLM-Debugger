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
        Connects a receiver to a signal.
        
        This method connects a receiver function to a signal. The receiver will be called
        whenever the signal is sent. The receiver can be a weak reference if specified.
        
        Parameters:
        receiver (function): The function to be called when the signal is sent.
        sender (object, optional): The sender of the signal. If not specified, the receiver
        will be called for all senders. Default is None.
        weak (bool, optional): Whether
        """

        self._lazy_method(
            super().connect, apps, receiver, sender,
            weak=weak, dispatch_uid=dispatch_uid,
        )

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None, apps=None):
        """
        Disconnects signal receivers from the specified sender.
        
        This method is a lazy wrapper around the original disconnect method of the superclass.
        
        Parameters:
        receiver (object, optional): The receiver function or class to disconnect. If not provided, all receivers will be disconnected.
        sender (object, optional): The sender object whose signals should be disconnected. If not provided, all senders will be disconnected.
        dispatch_uid (str, optional): A unique identifier for the connection to be disconnected. If not provided,
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
migrate = Signal()
post_migrate = Signal()
