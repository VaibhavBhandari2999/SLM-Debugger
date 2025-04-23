from pathlib import Path

from django.conf import settings

from . import Error, Tags, register


@register(Tags.files)
def check_setting_file_upload_temp_dir(app_configs, **kwargs):
    """
    Check the FILE_UPLOAD_TEMP_DIR setting for a valid directory.
    
    This function verifies if the `FILE_UPLOAD_TEMP_DIR` setting is defined and points to a valid directory. If the setting is set but the directory does not exist, it returns an error message.
    
    Parameters:
    app_configs (list): A list of AppConfig instances. This parameter is required by Django's app_config_ready signal and is not used in this function.
    **kwargs: Additional keyword arguments. This parameter is required by Django's app
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
