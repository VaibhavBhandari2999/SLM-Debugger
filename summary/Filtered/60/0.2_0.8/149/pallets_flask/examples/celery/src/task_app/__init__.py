from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    This function initializes a Flask application with the specified configuration and registers a blueprint for views. It also configures a Celery instance for background task processing.
    
    Parameters:
    None
    
    Returns:
    Flask: The configured Flask application instance.
    
    Key Components:
    - **Celery Configuration**: Sets up the Celery instance with a Redis broker and backend for task execution and result storage.
    - **Blueprint Registration**: Registers a blueprint for handling views, which includes routes and templates.
    -
    """

    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    from . import views

    app.register_blueprint(views.bp)
    return app


def celery_init_app(app: Flask) -> Celery:
    """
    Initialize a Celery instance with a Flask application.
    
    This function configures and initializes a Celery instance to work with a given Flask application. It sets up a custom task class that runs tasks within the Flask application context.
    
    Parameters:
    app (Flask): The Flask application to configure Celery for.
    
    Returns:
    Celery: The configured Celery instance.
    
    Key Components:
    - `FlaskTask`: A custom task class that runs tasks within the Flask application context.
    - `config
    """

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
