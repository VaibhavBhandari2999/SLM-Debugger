from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template


def create_app() -> Flask:
    """
    This function initializes and configures a Flask web application.
    
    Parameters:
    - None
    
    Returns:
    - Flask: A configured Flask web application instance.
    
    Key Components:
    - Configures the application with a Redis broker and result backend for Celery.
    - Registers a route for the root URL ("/") that renders an "index.html" template.
    - Registers a blueprint for views.
    
    Dependencies:
    - Flask
    - Flask-Celery
    - Jinja2 (for rendering templates)
    
    Usage:
    This function is typically called
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
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
