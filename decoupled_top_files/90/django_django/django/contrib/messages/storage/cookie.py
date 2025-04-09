"""
This Python file provides a custom Django message storage mechanism that stores messages in a cookie. It includes several classes and functions designed to handle the serialization, encoding, and decoding of these messages:

1. **MessageEncoder**: A custom JSON encoder that serializes `Message` objects into a compact JSON format.
2. **MessageDecoder**: A custom JSON decoder that processes JSON data containing serialized `Message` objects, marking safe HTML content appropriately.
3. **MessageSerializer**: A utility class for serializing and deserializing Python objects into JSON strings.
4. **CookieStorage**: A subclass of `BaseStorage` that stores messages in a cookie. It handles encoding, storing, and retrieving messages, ensuring that only a limited amount of data is stored in
"""
import binascii
import json

from django.conf import settings
from django.contrib.messages.storage.base import BaseStorage, Message
from django.core import signing
from django.http import SimpleCookie
from django.utils.safestring import SafeData, mark_safe


class MessageEncoder(json.JSONEncoder):
    """
    Compactly serialize instances of the ``Message`` class as JSON.
    """
    message_key = '__json_message'

    def default(self, obj):
        """
        Serializes an object into JSON format. If the object is an instance of `Message`, it converts it into a list containing the message key, a boolean indicating whether the message contains `SafeData`, the message level, and the message itself. If the object has extra tags, they are appended to the list. Otherwise, it falls back to the default serialization behavior.
        
        Args:
        obj (object): The object to be serialized.
        
        Returns:
        list or dict: A list if the
        """

        if isinstance(obj, Message):
            # Using 0/1 here instead of False/True to produce more compact json
            is_safedata = 1 if isinstance(obj.message, SafeData) else 0
            message = [self.message_key, is_safedata, obj.level, obj.message]
            if obj.extra_tags:
                message.append(obj.extra_tags)
            return message
        return super().default(obj)


class MessageDecoder(json.JSONDecoder):
    """
    Decode JSON that includes serialized ``Message`` instances.
    """

    def process_messages(self, obj):
        """
        Processes a given object (list or dictionary) containing messages.
        
        Args:
        obj (list or dict): The input object containing message data.
        
        Returns:
        list or dict: Processed object with safe HTML content marked.
        
        This function checks if the input object is a list or a dictionary. If it's a list, it verifies if the first element is `MessageEncoder.message_key`. If true, it marks the fourth element of the list as safe HTML using `mark_safe` and
        """

        if isinstance(obj, list) and obj:
            if obj[0] == MessageEncoder.message_key:
                if obj[1]:
                    obj[3] = mark_safe(obj[3])
                return Message(*obj[2:])
            return [self.process_messages(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self.process_messages(value)
                    for key, value in obj.items()}
        return obj

    def decode(self, s, **kwargs):
        decoded = super().decode(s, **kwargs)
        return self.process_messages(decoded)


class MessageSerializer:
    def dumps(self, obj):
        """
        dumps(obj) -> str
        
        Serializes a Python object (obj) into a JSON string using the MessageEncoder class for encoding. The resulting JSON string is encoded in 'latin-1' character encoding.
        
        Args:
        obj: The Python object to be serialized.
        
        Returns:
        A byte string representing the serialized JSON data in 'latin-1' encoding.
        """

        return json.dumps(
            obj,
            separators=(',', ':'),
            cls=MessageEncoder,
        ).encode('latin-1')

    def loads(self, data):
        return json.loads(data.decode('latin-1'), cls=MessageDecoder)


class CookieStorage(BaseStorage):
    """
    Store messages in a cookie.
    """
    cookie_name = 'messages'
    # uwsgi's default configuration enforces a maximum size of 4kb for all the
    # HTTP headers. In order to leave some room for other cookies and headers,
    # restrict the session cookie to 1/2 of 4kb. See #18781.
    max_cookie_size = 2048
    not_finished = '__messagesnotfinished__'
    key_salt = 'django.contrib.messages'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signer = signing.get_cookie_signer(salt=self.key_salt)

    def _get(self, *args, **kwargs):
        """
        Retrieve a list of messages from the messages cookie. If the
        not_finished sentinel value is found at the end of the message list,
        remove it and return a result indicating that not all messages were
        retrieved by this storage.
        """
        data = self.request.COOKIES.get(self.cookie_name)
        messages = self._decode(data)
        all_retrieved = not (messages and messages[-1] == self.not_finished)
        if messages and not all_retrieved:
            # remove the sentinel value
            messages.pop()
        return messages, all_retrieved

    def _update_cookie(self, encoded_data, response):
        """
        Either set the cookie with the encoded data if there is any data to
        store, or delete the cookie.
        """
        if encoded_data:
            response.set_cookie(
                self.cookie_name, encoded_data,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE or None,
                httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
        else:
            response.delete_cookie(
                self.cookie_name,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )

    def _store(self, messages, response, remove_oldest=True, *args, **kwargs):
        """
        Store the messages to a cookie and return a list of any messages which
        could not be stored.

        If the encoded data is larger than ``max_cookie_size``, remove
        messages until the data fits (these are the messages which are
        returned), and add the not_finished sentinel value to indicate as much.
        """
        unstored_messages = []
        encoded_data = self._encode(messages)
        if self.max_cookie_size:
            # data is going to be stored eventually by SimpleCookie, which
            # adds its own overhead, which we must account for.
            cookie = SimpleCookie()  # create outside the loop

            def stored_length(val):
                return len(cookie.value_encode(val)[1])

            while encoded_data and stored_length(encoded_data) > self.max_cookie_size:
                if remove_oldest:
                    unstored_messages.append(messages.pop(0))
                else:
                    unstored_messages.insert(0, messages.pop())
                encoded_data = self._encode(messages + [self.not_finished],
                                            encode_empty=unstored_messages)
        self._update_cookie(encoded_data, response)
        return unstored_messages

    def _encode(self, messages, encode_empty=False):
        """
        Return an encoded version of the messages list which can be stored as
        plain text.

        Since the data will be retrieved from the client-side, the encoded data
        also contains a hash to ensure that the data was not tampered with.
        """
        if messages or encode_empty:
            return self.signer.sign_object(messages, serializer=MessageSerializer, compress=True)

    def _decode(self, data):
        """
        Safely decode an encoded text stream back into a list of messages.

        If the encoded text stream contained an invalid hash or was in an
        invalid format, return None.
        """
        if not data:
            return None
        try:
            return self.signer.unsign_object(data, serializer=MessageSerializer)
        except (signing.BadSignature, binascii.Error, json.JSONDecodeError):
            pass
        # Mark the data as used (so it gets removed) since something was wrong
        # with the data.
        self.used = True
        return None
