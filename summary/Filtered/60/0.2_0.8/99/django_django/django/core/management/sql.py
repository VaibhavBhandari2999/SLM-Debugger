import sys

from django.apps import apps
from django.db import models


def sql_flush(style, connection, reset_sequences=True, allow_cascade=False):
    """
    Return a list of the SQL statements used to flush the database.
    """
    tables = connection.introspection.django_table_names(
        only_existing=True, include_views=False
    )
    return connection.ops.sql_flush(
        style,
        tables,
        reset_sequences=reset_sequences,
        allow_cascade=allow_cascade,
    )


def emit_pre_migrate_signal(verbosity, interactive, db, **kwargs):
    """
    Emit the pre_migrate signal for every application.
    
    This function iterates over all application configurations and sends a pre_migrate signal for each one. The signal is sent with the application configuration as the sender, and includes the verbosity, interactive status, and database name as parameters.
    
    Parameters:
    verbosity (int): The verbosity level for output messages.
    interactive (bool): Whether the command is being run interactively.
    db (str): The database name to use for the migration.
    
    Keyword Arguments
    """

    # Emit the pre_migrate signal for every application.
    for app_config in apps.get_app_configs():
        if app_config.models_module is None:
            continue
        if verbosity >= 2:
            stdout = kwargs.get("stdout", sys.stdout)
            stdout.write(
                "Running pre-migrate handlers for application %s" % app_config.label
            )
        models.signals.pre_migrate.send(
            sender=app_config,
            app_config=app_config,
            verbosity=verbosity,
            interactive=interactive,
            using=db,
            **kwargs,
        )


def emit_post_migrate_signal(verbosity, interactive, db, **kwargs):
    # Emit the post_migrate signal for every application.
    for app_config in apps.get_app_configs():
        if app_config.models_module is None:
            continue
        if verbosity >= 2:
            stdout = kwargs.get("stdout", sys.stdout)
            stdout.write(
                "Running post-migrate handlers for application %s" % app_config.label
            )
        models.signals.post_migrate.send(
            sender=app_config,
            app_config=app_config,
            verbosity=verbosity,
            interactive=interactive,
            using=db,
            **kwargs,
        )
