"""
The provided Python file contains definitions for logging levels and their corresponding tags. It includes constants for different logging levels (DEBUG, INFO, SUCCESS, WARNING, ERROR) and a dictionary mapping these levels to their respective tags. This file serves as a configuration module for a logging system, providing a standardized way to categorize log messages based on their severity.

### Docstring:
```python
"""
DEBUG = 10
INFO = 20
SUCCESS = 25
WARNING = 30
ERROR = 40

DEFAULT_TAGS = {
    DEBUG: 'debug',
    INFO: 'info',
    SUCCESS: 'success',
    WARNING: 'warning',
    ERROR: 'error',
}

DEFAULT_LEVELS = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'SUCCESS': SUCCESS,
    'WARNING': WARNING,
    'ERROR': ERROR,
}
