"""
This Python file is part of a Django application's database migration framework. It imports and defines several key components used for managing database schema changes and migrations.

#### Classes Defined:
1. **Migration**: A base class for defining individual database migrations.
2. **swappable_dependency**: A utility function to handle dependencies on swappable models.

#### Functions Defined:
- All functions from the `operations` module are imported, indicating they are used for various operations during migration execution.

#### Key Responsibilities:
- **Migration Class**: Represents a single migration step, containing operations to alter the database schema.
- **swappable_dependency Function**: Helps manage dependencies on models that can be swapped out at runtime, ensuring migrations work correctly even if model names change.

#### Interactions:
"""
from .migration import Migration, swappable_dependency  # NOQA
from .operations import *  # NOQA
