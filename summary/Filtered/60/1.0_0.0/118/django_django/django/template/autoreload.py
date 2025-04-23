from pathlib import Path

from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils._os import to_path
from django.utils.autoreload import autoreload_started, file_changed, is_django_path


def get_template_directories():
    """
    Retrieve a set of template directories.
    
    This function iterates through each template backend and collects directories
    that have a 'get_dirs' method, excluding Django templates. It returns a set
    of paths to template directories.
    
    Parameters:
    None
    
    Returns:
    set: A set of paths to template directories.
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
    Reset Django template loaders when a template file is modified.
    
    This function is triggered when a file is saved in the Django project. It checks if the saved file is a Python file or a template file located in one of the template directories. If the file is a template file, it resets the Django template loaders.
    
    Parameters:
    sender (str): The sender of the signal, typically the model instance that triggered the signal.
    file_path (pathlib.Path): The path to the file that was saved
    """

    if file_path.suffix == ".py":
        return
    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
