"""
This Python file imports several modules from a package related to database extensions for PostgreSQL. It includes support for arrays, CITEXT, hstore, JSONB, and range types which are common PostgreSQL extensions used for storing complex data structures and text with case-insensitive comparison.

The file does not define any new classes or functions itself, but rather serves as an import statement for these database extension functionalities. Users can directly access the functionality provided by these imported modules without needing to import them individually.

Key responsibilities:
- Provide a convenient way to import multiple PostgreSQL database extension functionalities in one line.
- Ensure that users have access to advanced data types like arrays, case-insensitive text, key-value stores, JSON objects, and range types.

### Docstring:
```python
"""
from .array import *  # NOQA
from .citext import *  # NOQA
from .hstore import *  # NOQA
from .jsonb import *  # NOQA
from .ranges import *  # NOQA
