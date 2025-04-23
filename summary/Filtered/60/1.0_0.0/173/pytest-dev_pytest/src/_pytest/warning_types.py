import attr


class PytestWarning(UserWarning):
    """
    Bases: :class:`UserWarning`.

    Base class for all warnings emitted by pytest.
    """

    __module__ = "pytest"


class PytestAssertRewriteWarning(PytestWarning):
    """
    Bases: :class:`PytestWarning`.

    Warning emitted by the pytest assert rewrite module.
    """

    __module__ = "pytest"


class PytestCacheWarning(PytestWarning):
    """
    Bases: :class:`PytestWarning`.

    Warning emitted by the cache plugin in various situations.
    """

    __module__ = "pytest"


class PytestConfigWarning(PytestWarning):
    """
    Bases: :class:`PytestWarning`.

    Warning emitted for configuration issues.
    """

    __module__ = "pytest"


class PytestCollectionWarning(PytestWarning):
    """
    Bases: :class:`PytestWarning`.

    Warning emitted when pytest is not able to collect a file or symbol in a module.
    """

    __module__ = "pytest"


class PytestDeprecationWarning(PytestWarning, DeprecationWarning):
    """
    Bases: :class:`pytest.PytestWarning`, :class:`DeprecationWarning`.

    Warning class for features that will be removed in a future version.
    """

    __module__ = "pytest"


class PytestExperimentalApiWarning(PytestWarning, FutureWarning):
    """
    Bases: :class:`pytest.PytestWarning`, :class:`FutureWarning`.

    Warning category used to denote experiments in pytest. Use sparingly as the API might change or even be
    removed completely in future version
    """

    __module__ = "pytest"

    @classmethod
    def simple(cls, apiname):
        """
        Generates a simple warning message for an experimental API.
        
        This function creates a warning message indicating that the specified API is experimental and may change over time.
        
        Parameters:
        cls (type): The class to which the warning message will be attached.
        apiname (str): The name of the API that is experimental.
        
        Returns:
        str: A formatted warning message indicating that the API is experimental.
        """

        return cls(
            "{apiname} is an experimental api that may change over time".format(
                apiname=apiname
            )
        )


class PytestUnhandledCoroutineWarning(PytestWarning):
    """
    Bases: :class:`PytestWarning`.

    Warning emitted when pytest encounters a test function which is a coroutine,
    but it was not handled by any async-aware plugin. Coroutine test functions
    are not natively supported.
    """

    __module__ = "pytest"


class PytestUnknownMarkWarning(PytestWarning):
    """
    Bases: :class:`PytestWarning`.

    Warning emitted on use of unknown markers.
    See https://docs.pytest.org/en/latest/mark.html for details.
    """

    __module__ = "pytest"


class RemovedInPytest4Warning(PytestDeprecationWarning):
    """
    Bases: :class:`pytest.PytestDeprecationWarning`.

    Warning class for features scheduled to be removed in pytest 4.0.
    """

    __module__ = "pytest"


@attr.s
class UnformattedWarning:
    """Used to hold warnings that need to format their message at runtime, as opposed to a direct message.

    Using this class avoids to keep all the warning types and messages in this module, avoiding misuse.
    """

    category = attr.ib()
    template = attr.ib()

    def format(self, **kwargs):
        """Returns an instance of the warning category, formatted with given kwargs"""
        return self.category(self.template.format(**kwargs))


PYTESTER_COPY_EXAMPLE = PytestExperimentalApiWarning.simple("testdir.copy_example")
