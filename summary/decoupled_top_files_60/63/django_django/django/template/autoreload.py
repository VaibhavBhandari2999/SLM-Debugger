from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils.autoreload import (
    autoreload_started, file_changed, is_django_path,
)


def get_template_directories():
    """
    Retrieve template directories from all configured template backends.
    
    This function iterates through each template backend, collecting directories
    from template loaders that have a 'get_dirs' method. It filters out Django
    template directories and returns a set of unique directories.
    
    Parameters:
    None
    
    Returns:
    set: A set of template directories from all configured backends, excluding Django templates.
    """

    # Iterate through each template backend and find
    # any template_loader that has a 'get_dirs' method.
    # Collect the directories, filtering out Django templates.
    items = set()
    for backend in engines.all():
        if not isinstance(backend, DjangoTemplates):
            continue

        items.update(backend.engine.dirs)

        for loader in backend.engine.template_loaders:
            if not hasattr(loader, 'get_dirs'):
                continue
            items.update(
                directory
                for directory in loader.get_dirs()
                if not is_django_path(directory)
            )
    return items


def reset_loaders():
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
    Reset Django template loaders when a template file in a specified directory is changed.
    
    Parameters:
    sender (str): The model or object that triggered the signal.
    file_path (Path): The path to the changed template file.
    **kwargs: Additional keyword arguments passed to the signal handler.
    
    Returns:
    bool: True if the template loaders were reset, False otherwise.
    
    This function checks if the changed template file is located within any of the directories specified by `get_template_directories()`. If
    """

    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
