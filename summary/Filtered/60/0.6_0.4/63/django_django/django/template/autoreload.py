from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils.autoreload import (
    autoreload_started, file_changed, is_django_path,
)


def get_template_directories():
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
    """
    Resets the template loaders for all DjangoTemplates backends in the engines.
    
    This function iterates over all backends registered in the Django engine. It checks if a backend is an instance of DjangoTemplates. If so, it proceeds to reset the template loaders for that backend.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example usage:
    reset_loaders()
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
    Reset Django template loaders when a template file in a specified directory is changed.
    
    This function is triggered when a template file is changed. It checks if the file path is within any of the template directories specified in Django settings. If the file is found in one of these directories, it resets the template loaders to ensure that the latest templates are used.
    
    Parameters:
    sender (str): The model or object that triggered the signal.
    file_path (Path): The file path of the changed template file
    """

    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
