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
        Connects a receiver function to a signal.
        
        This method connects a receiver function to a signal. It supports lazy evaluation and can be used in a settings file.
        
        Parameters:
        receiver (function): The function to be connected as a receiver.
        sender (type, optional): The sender of the signal. If not provided, the receiver will be connected to all senders. Defaults to None.
        weak (bool, optional): Whether to use a weak reference to the receiver. If True, the
        """

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
        Disconnects signal handlers.
        
        This method disconnects signal handlers previously connected using the same `receiver` and `sender` arguments. If `dispatch_uid` is provided, only the handler connected with that `dispatch_uid` will be disconnected. If `apps` is provided, it should be a list of app labels to filter the signals to be disconnected.
        
        Parameters:
        receiver (object, optional): The receiver function or callable that was used to connect the signal. Defaults to None.
        sender (object
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

post_migrate = Signal()
