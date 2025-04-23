from pathlib import Path

from django.conf import settings

from . import Error, Tags, register


@register(Tags.files)
def check_setting_file_upload_temp_dir(app_configs, **kwargs):
    """
    Function to validate the FILE_UPLOAD_TEMP_DIR setting.
    
    This function checks if the FILE_UPLOAD_TEMP_DIR setting is correctly configured. It ensures that the specified directory exists.
    
    Parameters:
    app_configs (list): A list of AppConfig instances. This parameter is required by Django's app_config_ready signal and is not used in this function.
    **kwargs: Additional keyword arguments. This parameter is required by Django's app_config_ready signal and is not used in this function.
    
    Returns:
    list: A list of
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
