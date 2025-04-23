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
        
        This function is designed to execute a method on a receiver object in a lazy manner, meaning the method is not immediately called but is scheduled for execution at a later time. It supports both model and app-level operations.
        
        Parameters:
        method (callable): The method to be executed on the receiver.
        apps (list, optional): A list of app labels to which the operation should be applied. Defaults to None.
        receiver (object): The object on which the
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
        
        This method connects a receiver function to a signal. The receiver function will be called when the signal is sent. The receiver can be a callable object or a string that names a function.
        
        Parameters:
        receiver (callable or str): The receiver function or the name of the function to be called when the signal is sent.
        sender (type, optional): The sender of the signal. If provided, the receiver will only be connected to signals sent by this
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
te = Signal()
