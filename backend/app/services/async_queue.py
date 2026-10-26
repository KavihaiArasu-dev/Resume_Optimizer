"""
Asynchronous Job Queue and Progress Tracking Service.
Provides thread/task safe job tracking with incremental progress and status reporting.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable


class AsyncTaskQueue:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, name: str = "Optimization Job") -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "task_id": task_id,
            "name": name,
            "status": "pending",  # pending, processing, completed, failed
            "progress": 0,        # 0 to 100
            "step": "Initialized",
            "result": None,
            "error": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return task_id

    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        step: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        if task_id not in self._tasks:
            return
        task = self._tasks[task_id]
        if status is not None:
            task["status"] = status
        if progress is not None:
            task["progress"] = min(100, max(0, progress))
        if step is not None:
            task["step"] = step
        if result is not None:
            task["result"] = result
        if error is not None:
            task["error"] = error
        task["updated_at"] = datetime.utcnow().isoformat()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)


# Global task queue singleton
task_queue = AsyncTaskQueue()
