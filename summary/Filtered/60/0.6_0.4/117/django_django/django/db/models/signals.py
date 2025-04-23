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
        Lazy execution of a model method.
        
        This function defers the execution of a model method until the model is accessed. It takes a method, a list of apps, a receiver, and a sender as parameters. The method is applied to the receiver with additional keyword arguments. If the sender is a string, it is interpreted as a model name and the function schedules the method to be executed on the model. If the sender is an instance, the method is executed immediately on that instance.
        
        Parameters:
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
        Disconnects signal receivers from the specified sender.
        
        This method allows you to disconnect signal receivers from a specific sender. It accepts the following parameters:
        - `receiver`: The receiver function or class to disconnect (optional).
        - `sender`: The sender instance or class to disconnect from (optional).
        - `dispatch_uid`: A unique identifier to specify which connection to disconnect (optional).
        - `apps`: An optional parameter to pass to the underlying signal dispatcher.
        
        Returns:
        - The result of the underlying signal dispatcher's
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
