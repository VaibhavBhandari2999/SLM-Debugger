from pathlib import Path

from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils._os import to_path
from django.utils.autoreload import autoreload_started, file_changed, is_django_path


def get_template_directories():
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
    Resets all template loaders in the Django environment.
    
    This function iterates over all available template backends and resets the template loaders for each backend that is an instance of DjangoTemplates. The reset operation is performed on each loader to clear any cached data or state.
    
    Parameters:
    None
    
    Returns:
    None
    
    Note:
    This function is designed to be used in a Django environment where template caching or loading state needs to be cleared.
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
    """
    Reset Django template loaders when a non-Python template file is modified.
    
    This function is triggered by a file change event. It checks if the modified file is a template file (excluding Python files) and if it is located within any of the configured template directories. If both conditions are met, it resets the Django template loaders.
    
    Parameters:
    sender (str): The sender of the file change event.
    file_path (pathlib.Path): The path to the modified file.
    **kwargs: Additional
    """

    if file_path.suffix == ".py":
        return
    for template_dir in get_template_directories():
        if template_dir in file_path.parents:
            reset_loaders()
            return True
