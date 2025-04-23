from pathlib import Path

from django.conf import settings

from . import Error, Tags, register


@register(Tags.files)
def check_setting_file_upload_temp_dir(app_configs, **kwargs):
    """
    Function to validate the FILE_UPLOAD_TEMP_DIR setting.
    
    This function checks if the FILE_UPLOAD_TEMP_DIR setting is defined and if it points to a valid directory. If the setting is invalid, it returns a list of error messages. Otherwise, it returns an empty list.
    
    Parameters:
    - app_configs: Configuration objects for installed applications.
    - kwargs: Additional keyword arguments.
    
    Returns:
    - A list of django.core.checks.Error objects if the setting is invalid, otherwise an empty list.
    
    Key Points:
    - The
    """

    setting = getattr(settings, "FILE_UPLOAD_TEMP_DIR", None)
    if setting and not Path(setting).is_dir():
        return [
            Error(
                f"The FILE_UPLOAD_TEMP_DIR setting refers to the nonexistent "
                f"directory '{setting}'.",
                id="files.E001",
            ),
        ]
    return []
