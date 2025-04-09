"""
```markdown
This Python script configures Django admin interfaces for managing media, contact information, and episodes. It defines custom admin models and inlines to handle related objects. The primary responsibilities include registering models with the admin site and specifying how inline objects should be displayed and managed.
```

### Docstring:
```python
"""
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
    Category, Contact, Episode, EpisodePermanent, Media, PhoneNumber,
)

site = admin.AdminSite(name="admin")


class MediaInline(GenericTabularInline):
    model = Media


class EpisodeAdmin(admin.ModelAdmin):
    inlines = [
        MediaInline,
    ]


class PhoneNumberInline(GenericTabularInline):
    model = PhoneNumber


class MediaPermanentInline(GenericTabularInline):
    model = Media
    can_delete = False


site.register(Episode, EpisodeAdmin)
site.register(Contact, inlines=[PhoneNumberInline])
site.register(Category)
site.register(EpisodePermanent, inlines=[MediaPermanentInline])
