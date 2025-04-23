from pathlib import Path

from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils._os import to_path
from django.utils.autoreload import (
    autoreload_started, file_changed, is_django_path,
)


def get_template_directories():
    """
    Retrieve a set of template directories.
    
    This function iterates through each template backend and collects directories
    where templates are stored. It filters out directories associated with Django
    templates and ensures that only relevant directories are included.
    
    Parameters:
    None
    
    Returns:
    set: A set of template directories as Path objects, excluding Django templates.
    """

    # Iterate through each template backend and find
    # any template_loader that has a 'get_dirs' method.
    # Collect the directories, filtering out Django templates.
    cwd = Path.cwd()
    items = set()
    for backend in engines.all():
        if not isinstance(backend, DjangoTemplates):
            continue

        items.update(cwd / to_path(dir) for dir in backend.engine.dirs)

        for loader in backend.engine.template_loaders:
            if not hasattr(loader, 'get_dirs'):
                continue
            items.update(
                cwd / to_path(directory)
                for directory in loader.get_dirs()
                if not is_django_path(directory)
            )
    return items


def reset_loaders():
    """
    Reset the template loaders for all DjangoTemplates backends.
    
    This function iterates over all available template backends and resets the template loaders for those that are instances of DjangoTemplates. The reset operation is performed on each loader within the backend's engine.
    
    Parameters:
    None
    
    Returns:
    None
    
    Note:
    This function is designed to be used in Django environments where template loaders need to be refreshed or reloaded.
    """

    for backend in engines.all():
        if not isinstance(backend, DjangoTemplates):
            continue
        for loader in backend.engine.template_loaders:
            loader.reset()


@receiver(autoreload_started, dispatch_uid='template_loaders_watch_changes')
def watch_for_template_changes(sender, **kwargs):
    for directory in get_template_directories():
        sender.watch_dir(directory, '**/*')


@receiver(file_changed, dispatch_uid='template_loaders_file_changed')
def template_changed(sender, file_path, **kwargs):
    """
    Reset Django template loaders when a template file in a specific directory is changed.
    
    This function is triggered when a template file is changed. It checks if the file path is within any of the template directories specified in Django settings. If the file is found within one of these directories, it resets the template loaders to ensure that the changes are picked up.
    
    Parameters:
    sender (str): The model or object that triggered the signal.
    file_path (Path): The path to the changed template file.
    
    Returns
    """

    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
