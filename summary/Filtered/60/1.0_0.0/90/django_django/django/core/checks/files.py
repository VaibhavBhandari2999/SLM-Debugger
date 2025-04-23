from pathlib import Path

from django.conf import settings

from . import Error, Tags, register


@register(Tags.files)
def check_setting_file_upload_temp_dir(app_configs, **kwargs):
    """
    Function to validate the FILE_UPLOAD_TEMP_DIR setting.
    
    This function checks if the FILE_UPLOAD_TEMP_DIR setting is set and if the specified directory exists.
    
    Parameters:
    - app_configs: Configuration objects for installed applications. Not used in this function.
    - kwargs: Additional keyword arguments. Not used in this function.
    
    Returns:
    - A list of Django error objects if the setting is invalid, otherwise an empty list.
    
    Key Points:
    - The function uses the `settings` object to retrieve the FILE_UPLOAD_TEMP_DIR setting
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
