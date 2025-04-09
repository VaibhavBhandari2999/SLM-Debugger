"""
The provided Python file defines a `FileProxyMixin` class which acts as a proxy for file operations. It allows methods from an underlying file object to be accessed through instances of classes that inherit from `FileProxyMixin`. This is particularly useful for adding additional functionality or wrapping file objects without modifying their original implementation.

#### Main Components:
- **FileProxyMixin**: A mixin class that provides a way to forward file methods to an underlying file object named `file`.
- **Properties**:
  - `encoding`, `fileno`, `flush`, `isatty`, `newlines`, `read`, `readinto`, `readline`, `readlines`, `seek`, `tell`, `truncate`, `write`, `writelines`: These
"""
class FileProxyMixin:
    """
    A mixin class used to forward file methods to an underlaying file
    object.  The internal file object has to be called "file"::

        class FileProxy(FileProxyMixin):
            def __init__(self, file):
                self.file = file
    """

    encoding = property(lambda self: self.file.encoding)
    fileno = property(lambda self: self.file.fileno)
    flush = property(lambda self: self.file.flush)
    isatty = property(lambda self: self.file.isatty)
    newlines = property(lambda self: self.file.newlines)
    read = property(lambda self: self.file.read)
    readinto = property(lambda self: self.file.readinto)
    readline = property(lambda self: self.file.readline)
    readlines = property(lambda self: self.file.readlines)
    seek = property(lambda self: self.file.seek)
    tell = property(lambda self: self.file.tell)
    truncate = property(lambda self: self.file.truncate)
    write = property(lambda self: self.file.write)
    writelines = property(lambda self: self.file.writelines)

    @property
    def closed(self):
        return not self.file or self.file.closed

    def readable(self):
        """
        Determines if the file is readable.
        
        Args:
        self (File): The file object to check.
        
        Returns:
        bool: True if the file is readable, False otherwise.
        
        Notes:
        - Checks if the file is closed.
        - Uses the `readable` method of the file object if available.
        """

        if self.closed:
            return False
        if hasattr(self.file, 'readable'):
            return self.file.readable()
        return True

    def writable(self):
        """
        Determines if the file is writable.
        
        Args:
        self: The file object to check.
        
        Returns:
        bool: True if the file is writable, False otherwise.
        
        Notes:
        - Checks if the file is closed.
        - Uses the `writable` method of the file object if available.
        - Otherwise, checks if the mode of the file contains 'w'.
        """

        if self.closed:
            return False
        if hasattr(self.file, 'writable'):
            return self.file.writable()
        return 'w' in getattr(self.file, 'mode', '')

    def seekable(self):
        """
        Determines if the file is seekable.
        
        Args:
        self: The file object to check.
        
        Returns:
        bool: True if the file is seekable, False otherwise.
        
        Notes:
        - Checks if the file is closed.
        - Uses the `seekable` method of the file object if available.
        """

        if self.closed:
            return False
        if hasattr(self.file, 'seekable'):
            return self.file.seekable()
        return True

    def __iter__(self):
        return iter(self.file)
