from pathlib import Path

from django.dispatch import receiver
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.utils._os import to_path
from django.utils.autoreload import autoreload_started, file_changed, is_django_path


def get_template_directories():
    """
    Retrieve a set of template directories from the configured template backends.
    
    This function iterates through each template backend configured in Django,
    filtering out the Django template backend. For each non-Django template backend,
    it collects the directories where templates are stored, ensuring to exclude
    Django's built-in template directories. Additionally, it checks each template
    loader for a 'get_dirs' method and collects the directories returned by this
    method, again filtering out Django's built-in directories.
    
    Parameters:
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
    Resets the template loaders in the Django environment.
    
    This function iterates through all available template backends and resets the template loaders for any backend that is not an instance of DjangoTemplates.
    
    Parameters:
    None
    
    Returns:
    None
    
    Explanation:
    This function is used to clear the cached templates in Django's template loaders. It is useful when you want to ensure that the latest templates are being used without restarting the server. The function loops through all available template backends and checks if they are instances
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
