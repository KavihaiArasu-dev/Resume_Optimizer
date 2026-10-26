"""
Async Tasks API Router.
GET /api/tasks/{task_id}
"""
from fastapi import APIRouter, HTTPException
from app.services.async_queue import task_queue
from app.schemas.schemas import TaskStatusResponse

router = APIRouter()


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the progress and result of an async background job."""
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        step=task["step"],
        result=task.get("result"),
        error=task.get("error"),
    )
