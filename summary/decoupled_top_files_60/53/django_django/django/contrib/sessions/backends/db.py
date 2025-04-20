import logging

from django.contrib.sessions.backends.base import (
    CreateError, SessionBase, UpdateError,
)
from django.core.exceptions import SuspiciousOperation
from django.db import DatabaseError, IntegrityError, router, transaction
from django.utils import timezone
from django.utils.functional import cached_property


class SessionStore(SessionBase):
    """
    Implement database session store.
    """
    def __init__(self, session_key=None):
        super().__init__(session_key)

    @classmethod
    def get_model_class(cls):
        """
        Retrieve the model class for Django session objects.
        
        This function returns the model class for session objects, which is used to
        interact with session data stored in the database. It avoids a circular import
        and allows importing SessionStore even when django.contrib.sessions is not
        included in INSTALLED_APPS.
        
        Parameters:
        cls (type): The class object from which to derive the session model class.
        
        Returns:
        type: The model class for session objects.
        
        Example:
        >>> from django.contrib.sessions.models import
        """

        # Avoids a circular import and allows importing SessionStore when
        # django.contrib.sessions is not in INSTALLED_APPS.
        from django.contrib.sessions.models import Session
        return Session

    @cached_property
    def model(self):
        return self.get_model_class()

    def _get_session_from_db(self):
        try:
            return self.model.objects.get(
                session_key=self.session_key,
                expire_date__gt=timezone.now()
            )
        except (self.model.DoesNotExist, SuspiciousOperation) as e:
            if isinstance(e, SuspiciousOperation):
                logger = logging.getLogger('django.security.%s' % e.__class__.__name__)
                logger.warning(str(e))
            self._session_key = None

    def load(self):
        s = self._get_session_from_db()
        return self.decode(s.session_data) if s else {}

    def exists(self, session_key):
        return self.model.objects.filter(session_key=session_key).exists()

    def create(self):
        """
        Creates a new instance of the model.
        
        This method generates a new session key and attempts to save the instance
        to the database. If the session key is not unique, the method will continue
        to generate new keys until a unique one is found. Once a unique key is
        obtained, the instance is marked as modified and returned.
        
        Parameters:
        None
        
        Returns:
        The modified instance of the model.
        
        Raises:
        CreateError: If the instance cannot be saved due to a unique
        """

        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            return

    def create_model_instance(self, data):
        """
        Return a new instance of the session model object, which represents the
        current session state. Intended to be used for saving the session data
        to the database.
        """
        return self.model(
            session_key=self._get_or_create_session_key(),
            session_data=self.encode(data),
            expire_date=self.get_expiry_date(),
        )

    def save(self, must_create=False):
        """
        Save the current session data to the database. If 'must_create' is
        True, raise a database error if the saving operation doesn't create a
        new entry (as opposed to possibly updating an existing entry).
        """
        if self.session_key is None:
            return self.create()
        data = self._get_session(no_load=must_create)
        obj = self.create_model_instance(data)
        using = router.db_for_write(self.model, instance=obj)
        try:
            with transaction.atomic(using=using):
                obj.save(force_insert=must_create, force_update=not must_create, using=using)
        except IntegrityError:
            if must_create:
                raise CreateError
            raise
        except DatabaseError:
            if not must_create:
                raise UpdateError
            raise

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.model.objects.get(session_key=session_key).delete()
        except self.model.DoesNotExist:
            pass

    @classmethod
    def clear_expired(cls):
        cls.get_model_class().objects.filter(expire_date__lt=timezone.now()).delete()
