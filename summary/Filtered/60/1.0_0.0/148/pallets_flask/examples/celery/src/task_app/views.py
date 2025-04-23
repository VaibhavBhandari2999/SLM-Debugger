from celery.result import AsyncResult
from flask import Blueprint
from flask import request

from . import tasks

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }


@bp.post("/add")
def add() -> dict[str, object]:
    """
    Add two numbers and return a result object.
    
    This function takes two integer parameters, 'a' and 'b', from the request form data. It uses a task (presumably a background task) to add these numbers and returns a dictionary containing the task result ID.
    
    Parameters:
    a (int): The first number to add. Defaults to the value of 'a' from the request form data.
    b (int): The second number to add. Defaults to the value of 'b'
    """

    a = request.form.get("a", type=int)
    b = request.form.get("b", type=int)
    result = tasks.add.delay(a, b)
    return {"result_id": result.id}


@bp.post("/block")
def block() -> dict[str, object]:
    result = tasks.block.delay()
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    result = tasks.process.delay(total=request.form.get("total", type=int))
    return {"result_id": result.id}
et("total", type=int))
    return {"result_id": result.id}
