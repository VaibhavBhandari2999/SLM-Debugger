"""
This Python script defines two classes, `File` and `ContentFile`, along with utility functions for handling file-like objects. The `File` class provides methods for reading and manipulating file objects, including determining their size, reading in chunks, and iterating over lines. The `ContentFile` class is a specialized subclass of `File` designed to handle raw content directly, such as strings or bytes, without needing an actual file object. Utility functions `endswith_cr`, `endswith_lf`, and `equals_lf` are provided to assist in line-by-line processing of text or byte strings. The classes and functions together offer a flexible way to manage file-like objects, supporting both file-based and in-memory content. ```python
"""
import os
from io import BytesIO, StringIO, UnsupportedOperation

from django.core.files.utils import FileProxyMixin
from django.utils.functional import cached_property


class File(FileProxyMixin):
    DEFAULT_CHUNK_SIZE = 64 * 2 ** 10

    def __init__(self, file, name=None):
        """
        Initialize a new instance of the class.
        
        Args:
        file (file): The file object to be used.
        name (str, optional): The name of the file. Defaults to the value of `file.name` if not provided.
        
        Attributes:
        file (file): The file object.
        name (str): The name of the file.
        mode (str, optional): The mode in which the file was opened, if available.
        """

        self.file = file
        if name is None:
            name = getattr(file, 'name', None)
        self.name = name
        if hasattr(file, 'mode'):
            self.mode = file.mode

    def __str__(self):
        return self.name or ''

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")

    def __bool__(self):
        return bool(self.name)

    def __len__(self):
        return self.size

    @cached_property
    def size(self):
        """
        Determines the size of a file.
        
        Args:
        self: The instance of the class containing the file attribute.
        
        Returns:
        int: The size of the file in bytes.
        
        Raises:
        AttributeError: If unable to determine the file's size.
        
        Notes:
        - Utilizes `hasattr` to check if the file object has specific attributes.
        - Uses `os.path.getsize` to get the file size from its name.
        - Seeks to the end of
        """

        if hasattr(self.file, 'size'):
            return self.file.size
        if hasattr(self.file, 'name'):
            try:
                return os.path.getsize(self.file.name)
            except (OSError, TypeError):
                pass
        if hasattr(self.file, 'tell') and hasattr(self.file, 'seek'):
            pos = self.file.tell()
            self.file.seek(0, os.SEEK_END)
            size = self.file.tell()
            self.file.seek(pos)
            return size
        raise AttributeError("Unable to determine the file's size.")

    def chunks(self, chunk_size=None):
        """
        Read the file and yield chunks of ``chunk_size`` bytes (defaults to
        ``File.DEFAULT_CHUNK_SIZE``).
        """
        chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        try:
            self.seek(0)
        except (AttributeError, UnsupportedOperation):
            pass

        while True:
            data = self.read(chunk_size)
            if not data:
                break
            yield data

    def multiple_chunks(self, chunk_size=None):
        """
        Return ``True`` if you can expect multiple chunks.

        NB: If a particular file representation is in memory, subclasses should
        always return ``False`` -- there's no good reason to read from memory in
        chunks.
        """
        return self.size > (chunk_size or self.DEFAULT_CHUNK_SIZE)

    def __iter__(self):
        """
        Iterate over the file-like object by newlines.
        
        Args:
        self: The file-like object to iterate over.
        
        Yields:
        bytes: Lines from the file-like object.
        
        Notes:
        - The function splits the content into chunks and iterates over them.
        - It handles line endings by checking for carriage return (\r) and line feed (\n) characters.
        - It yields lines that are complete, either ending with a newline character or a combination of \r
        """

        # Iterate over this file-like object by newlines
        buffer_ = None
        for chunk in self.chunks():
            for line in chunk.splitlines(True):
                if buffer_:
                    if endswith_cr(buffer_) and not equals_lf(line):
                        # Line split after a \r newline; yield buffer_.
                        yield buffer_
                        # Continue with line.
                    else:
                        # Line either split without a newline (line
                        # continues after buffer_) or with \r\n
                        # newline (line == b'\n').
                        line = buffer_ + line
                    # buffer_ handled, clear it.
                    buffer_ = None

                # If this is the end of a \n or \r\n line, yield.
                if endswith_lf(line):
                    yield line
                else:
                    buffer_ = line

        if buffer_ is not None:
            yield buffer_

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def open(self, mode=None):
        """
        Open the file specified by `self.name` in the given `mode` (or the current mode if not specified). If the file is already open, seek to the beginning. If the file exists, reopen it with the specified mode; otherwise, raise a ValueError.
        
        Args:
        mode (str, optional): The mode in which to open the file. Defaults to None.
        
        Returns:
        File: The opened file object.
        
        Raises:
        ValueError: If the file cannot be reopened
        """

        if not self.closed:
            self.seek(0)
        elif self.name and os.path.exists(self.name):
            self.file = open(self.name, mode or self.mode)
        else:
            raise ValueError("The file cannot be reopened.")
        return self

    def close(self):
        self.file.close()


class ContentFile(File):
    """
    A File-like object that takes just raw content, rather than an actual file.
    """
    def __init__(self, content, name=None):
        """
        Initialize a new instance of the class.
        
        Args:
        content (str or bytes): The content to be stored in the stream.
        name (str, optional): The name of the stream.
        
        Returns:
        None
        
        Summary:
        This method initializes a new instance of the class by creating a stream using either StringIO or BytesIO based on the type of the input content. It then sets the name of the stream and calculates its size.
        """

        stream_class = StringIO if isinstance(content, str) else BytesIO
        super().__init__(stream_class(content), name=name)
        self.size = len(content)

    def __str__(self):
        return 'Raw content'

    def __bool__(self):
        return True

    def open(self, mode=None):
        self.seek(0)
        return self

    def close(self):
        pass

    def write(self, data):
        self.__dict__.pop('size', None)  # Clear the computed size.
        return self.file.write(data)


def endswith_cr(line):
    """Return True if line (a text or bytestring) ends with '\r'."""
    return line.endswith('\r' if isinstance(line, str) else b'\r')


def endswith_lf(line):
    """Return True if line (a text or bytestring) ends with '\n'."""
    return line.endswith('\n' if isinstance(line, str) else b'\n')


def equals_lf(line):
    """Return True if line (a text or bytestring) equals '\n'."""
    return line == ('\n' if isinstance(line, str) else b'\n')
