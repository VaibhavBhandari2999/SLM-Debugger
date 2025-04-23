from pathlib import Path

from django.conf import settings

from . import Error, Tags, register


@register(Tags.files)
def check_setting_file_upload_temp_dir(app_configs, **kwargs):
    """
    Function to validate the FILE_UPLOAD_TEMP_DIR setting.
    
    This function checks if the FILE_UPLOAD_TEMP_DIR setting is set and if the specified directory exists. If the directory does not exist, it returns an error.
    
    Parameters:
    app_configs (list): A list of AppConfig instances for the application.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list of Django error instances if the directory does not exist, otherwise an empty list.
    """

    setting = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', None)
    if setting and not Path(setting).is_dir():
        return [
            Error(
                f"The FILE_UPLOAD_TEMP_DIR setting refers to the nonexistent "
                f"directory '{setting}'.",
                id="files.E001",
            ),
        ]
    return []
