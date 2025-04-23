from pathlib import Path

from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils._os import to_path
from django.utils.autoreload import autoreload_started, file_changed, is_django_path


def get_template_directories():
    """
    Retrieve a set of template directories from the configured template backends.
    
    This function iterates through each template backend and collects directories
    where templates are stored. It filters out directories associated with the
    Django template backend and any directories that are not valid paths.
    
    Parameters:
    None
    
    Returns:
    set: A set of pathlib.Path objects representing the template directories.
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
    """
    Reset Django template loaders when a non-Python file in a template directory is modified.
    
    Args:
    sender (str): The model or object that triggered the signal.
    file_path (pathlib.Path): The path to the file that was modified.
    
    Returns:
    bool: True if the file is in a template directory and not a Python file, otherwise False.
    
    Notes:
    This function is designed to be used as a signal receiver in Django. It checks if the modified file is in one of
    """

    if file_path.suffix == ".py":
        return
    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
