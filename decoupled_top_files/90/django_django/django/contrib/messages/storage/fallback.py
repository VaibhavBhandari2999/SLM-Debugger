"""
The provided Python file contains a Django application component that handles message storage. It defines a custom message storage class called `FallbackStorage` which extends `BaseStorage` from Django's message framework. 

**Classes Defined:**
1. **FallbackStorage**: A custom message storage class that tries to store messages in the first available backend and falls back to subsequent backends if the first one fails.

**Functions Defined:**
1. **__init__**: Initializes the `FallbackStorage` instance by creating instances of multiple storage backends and tracking which ones have been used.
2. **_get**: Retrieves messages from all storage backends, stopping early if a backend has already been used.
3. **_store**: Stores messages across multiple storage backends
"""
from django.contrib.messages.storage.base import BaseStorage
from django.contrib.messages.storage.cookie import CookieStorage
from django.contrib.messages.storage.session import SessionStorage


class FallbackStorage(BaseStorage):
    """
    Try to store all messages in the first backend. Store any unstored
    messages in each subsequent backend.
    """
    storage_classes = (CookieStorage, SessionStorage)

    def __init__(self, *args, **kwargs):
        """
        Initialize the object with the given arguments and keyword arguments.
        
        This method initializes the parent class using `super()` and then creates a list of storages based on the provided `storage_classes`. Each storage is instantiated with the same arguments and keyword arguments as the parent class. The `_used_storages` set is also initialized to keep track of the used storages.
        
        Args:
        *args: Variable length argument list passed to the parent class and storage classes.
        **kwargs: Arbitrary keyword
        """

        super().__init__(*args, **kwargs)
        self.storages = [storage_class(*args, **kwargs)
                         for storage_class in self.storage_classes]
        self._used_storages = set()

    def _get(self, *args, **kwargs):
        """
        Get a single list of messages from all storage backends.
        """
        all_messages = []
        for storage in self.storages:
            messages, all_retrieved = storage._get()
            # If the backend hasn't been used, no more retrieval is necessary.
            if messages is None:
                break
            if messages:
                self._used_storages.add(storage)
            all_messages.extend(messages)
            # If this storage class contained all the messages, no further
            # retrieval is necessary
            if all_retrieved:
                break
        return all_messages, all_retrieved

    def _store(self, messages, response, *args, **kwargs):
        """
        Store the messages and return any unstored messages after trying all
        backends.

        For each storage backend, any messages not stored are passed on to the
        next backend.
        """
        for storage in self.storages:
            if messages:
                messages = storage._store(messages, response, remove_oldest=False)
            # Even if there are no more messages, continue iterating to ensure
            # storages which contained messages are flushed.
            elif storage in self._used_storages:
                storage._store([], response)
                self._used_storages.remove(storage)
        return messages
