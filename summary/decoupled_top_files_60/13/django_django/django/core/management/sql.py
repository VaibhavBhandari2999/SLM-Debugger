from django.apps import apps
from django.db import models


def sql_flush(style, connection, only_django=False, reset_sequences=True, allow_cascade=False):
    """
    Return a list of the SQL statements used to flush the database.

    If only_django is True, only include the table names that have associated
    Django models and are in INSTALLED_APPS .
    """
    if only_django:
        tables = connection.introspection.django_table_names(only_existing=True, include_views=False)
    else:
        tables = connection.introspection.table_names(include_views=False)
    seqs = connection.introspection.sequence_list() if reset_sequences else ()
    statements = connection.ops.sql_flush(style, tables, seqs, allow_cascade)
    return statements


def emit_pre_migrate_signal(verbosity, interactive, db, **kwargs):
    """
    Emit the pre-migrate signal for every application.
    
    This function is called during the Django database migration process to notify
    applications that the migration is about to start. It iterates over all
    applications and sends a pre-migrate signal for each one.
    
    Parameters:
    verbosity (int): The level of detail to print to the console. Higher values
    indicate more detailed output.
    interactive (bool): Whether the user is expected to interact with the
    process.
    db (str):
    """

    # Emit the pre_migrate signal for every application.
    for app_config in apps.get_app_configs():
        if app_config.models_module is None:
            continue
        if verbosity >= 2:
            print("Running pre-migrate handlers for application %s" % app_config.label)
        models.signals.pre_migrate.send(
            sender=app_config,
            app_config=app_config,
            verbosity=verbosity,
            interactive=interactive,
            using=db,
            **kwargs
        )


def emit_post_migrate_signal(verbosity, interactive, db, **kwargs):
    """
    Emit the post_migrate signal for every application.
    
    This function is responsible for running post-migrate handlers for each application in the Django project. It iterates over all application configurations and sends a post_migrate signal for each one.
    
    Parameters:
    verbosity (int): The verbosity level of the output. Higher values provide more detailed output.
    interactive (bool): Whether the command is being run in an interactive shell.
    db (str): The database alias to use for the signal.
    
    Returns:
    """

    # Emit the post_migrate signal for every application.
    for app_config in apps.get_app_configs():
        if app_config.models_module is None:
            continue
        if verbosity >= 2:
            print("Running post-migrate handlers for application %s" % app_config.label)
        models.signals.post_migrate.send(
            sender=app_config,
            app_config=app_config,
            verbosity=verbosity,
            interactive=interactive,
            using=db,
            **kwargs
        )
