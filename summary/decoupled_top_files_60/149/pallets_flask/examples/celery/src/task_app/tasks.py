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
    
    This method updates the task's state progressively as it iterates from 1 to the specified total. It provides a detailed progress report at each step by updating the task's state with the current iteration number and the total number of iterations.
    
    Parameters:
    total (int): The total number of iterations to be processed.
    
    Returns:
    dict: A dictionary containing the final progress information, including the current and total number of iterations.
    """

    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    return {"current": total, "total": total}
