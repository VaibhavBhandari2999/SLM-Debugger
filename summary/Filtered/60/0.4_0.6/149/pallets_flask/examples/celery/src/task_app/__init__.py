from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template


def create_app() -> Flask:
    """
    This function initializes and returns a Flask application.
    
    Parameters:
    - None
    
    Returns:
    - Flask: A configured Flask application with a route for the index page and a configured Celery instance.
    
    Key Details:
    - Configures the application with a Celery instance using Redis as the broker and result backend.
    - Sets up a route at the root URL ("/") that renders an "index.html" template.
    - Registers a blueprint named 'views' with the application.
    
    Dependencies:
    - Flask
    - Flask-Cel
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
    Initialize Celery with a Flask application.
    
    This function configures and initializes a Celery instance to work with a Flask application. It sets up a custom task class that ensures the application context is active during task execution.
    
    Parameters:
    app (Flask): The Flask application to configure Celery for.
    
    Returns:
    Celery: The configured Celery instance.
    
    Key Parameters:
    - app (Flask): The Flask application to configure Celery for.
    
    Key Keywords:
    - task_cls (Task
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
