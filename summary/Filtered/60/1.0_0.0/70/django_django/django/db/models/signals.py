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
        
        This function is designed to execute a method on a receiver object in a lazy manner, meaning the method is not executed immediately but is deferred until the model operation is performed. It supports both string and model instance inputs for the sender parameter.
        
        Parameters:
        method (callable): The method to be called on the receiver object.
        apps (list): A list of Django apps to be used for lazy operations. Defaults to None.
        receiver (object): The object on
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
        Connects a receiver to a signal.
        
        This method connects a receiver function or method to a signal. The receiver will be called when the signal is sent.
        
        Parameters:
        receiver (function or method): The function or method to be connected as the receiver.
        sender (type or object, optional): The sender that will send the signal. If not specified, the receiver will be connected to all senders.
        weak (bool, optional): If True (default), the receiver will be stored as
        """

        self._lazy_method(
            super().connect, apps, receiver, sender,
            weak=weak, dispatch_uid=dispatch_uid,
        )

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None, apps=None):
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

pre_migrate = Signal()
post_migrate = Signal()
