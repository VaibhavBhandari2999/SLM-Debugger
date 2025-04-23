import time

from celery import shared_task
from celery import Task


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    return a + b


@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    """
    Process a task with a given total number of iterations.
    
    This method updates the task's state progressively and simulates work by sleeping for one second per iteration.
    
    Parameters:
    total (int): The total number of iterations to process.
    
    Returns:
    dict: A dictionary containing the current and total iteration counts.
    """

    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    return {"current": total, "total": total}
