from pathlib import Path

from django.conf import settings

from . import Error, Tags, register


@register(Tags.files)
def check_setting_file_upload_temp_dir(app_configs, **kwargs):
    """
    Function to validate the FILE_UPLOAD_TEMP_DIR setting.
    
    This function checks if the FILE_UPLOAD_TEMP_DIR setting is defined and if it points to a valid directory. If the setting is invalid, it returns an error message.
    
    Parameters:
    app_configs (list): A list of AppConfig instances for the application.
    **kwargs: Additional keyword arguments.
    
    Returns:
    list: A list of Django error messages if the setting is invalid, otherwise an empty list.
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
