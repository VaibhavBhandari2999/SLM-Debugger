"""
```markdown
# This Python script configures settings for testing static and media files in Django applications. It defines a dictionary `TEST_SETTINGS` containing various configuration options such as URLs, file paths, installed apps, and middleware. These settings are tailored for testing purposes and ensure that static and media files can be correctly served during tests.

The main components defined in this file are:

- **TEST_SETTINGS**: A dictionary containing key settings for testing static and media files in Django. This includes:
  - `MEDIA_URL`: URL prefix for serving media files.
  - `STATIC_URL`: URL prefix for serving static files.
  - `MEDIA_ROOT`: Directory where media files will be stored.
  - `STATIC_ROOT`: Directory where static files will be collected
"""
import os.path
from pathlib import Path

TEST_ROOT = os.path.dirname(__file__)

TEST_SETTINGS = {
    'MEDIA_URL': 'media/',
    'STATIC_URL': 'static/',
    'MEDIA_ROOT': os.path.join(TEST_ROOT, 'project', 'site_media', 'media'),
    'STATIC_ROOT': os.path.join(TEST_ROOT, 'project', 'site_media', 'static'),
    'STATICFILES_DIRS': [
        os.path.join(TEST_ROOT, 'project', 'documents'),
        ('prefix', os.path.join(TEST_ROOT, 'project', 'prefixed')),
        Path(TEST_ROOT) / 'project' / 'pathlib',
    ],
    'STATICFILES_FINDERS': [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.DefaultStorageFinder',
    ],
    'INSTALLED_APPS': [
        'django.contrib.staticfiles',
        'staticfiles_tests',
        'staticfiles_tests.apps.test',
        'staticfiles_tests.apps.no_label',
    ],
    # In particular, AuthenticationMiddleware can't be used because
    # contrib.auth isn't in INSTALLED_APPS.
    'MIDDLEWARE': [],
}
