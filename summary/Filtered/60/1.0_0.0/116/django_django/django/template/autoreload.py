from pathlib import Path

from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils._os import to_path
from django.utils.autoreload import autoreload_started, file_changed, is_django_path


def get_template_directories():
    """
    Retrieve template directories from configured template backends.
    
    This function iterates through each configured template backend and collects directories
    where templates are located. It filters out directories associated with Django's built-in
    template system and ensures that only directories from other template loaders are included.
    
    Parameters:
    None
    
    Returns:
    set: A set of pathlib.Path objects representing the directories where templates are located.
    """

    # Iterate through each template backend and find
    # any template_loader that has a 'get_dirs' method.
    # Collect the directories, filtering out Django templates.
    cwd = Path.cwd()
    items = set()
    for backend in engines.all():
        if not isinstance(backend, DjangoTemplates):
            continue

        items.update(cwd / to_path(dir) for dir in backend.engine.dirs if dir)

        for loader in backend.engine.template_loaders:
            if not hasattr(loader, "get_dirs"):
                continue
            items.update(
                cwd / to_path(directory)
                for directory in loader.get_dirs()
                if directory and not is_django_path(directory)
            )
    return items


def reset_loaders():
    """
    Resets the template loaders for all DjangoTemplates backends.
    
    This function iterates through all registered template engines, and for each DjangoTemplates backend, it resets the template loaders.
    
    Parameters:
    None
    
    Returns:
    None
    
    Note:
    This function is designed to be used in Django projects where template loaders need to be reset, typically after changes to template directories or files.
    """

    for backend in engines.all():
        if not isinstance(backend, DjangoTemplates):
            continue
        for loader in backend.engine.template_loaders:
            loader.reset()


@receiver(autoreload_started, dispatch_uid="template_loaders_watch_changes")
def watch_for_template_changes(sender, **kwargs):
    for directory in get_template_directories():
        sender.watch_dir(directory, "**/*")


@receiver(file_changed, dispatch_uid="template_loaders_file_changed")
def template_changed(sender, file_path, **kwargs):
    if file_path.suffix == ".py":
        return
    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
