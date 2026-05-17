from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .tasks import heavy_computation
from celery.result import AsyncResult
from .celery_worker import celery_app

app = FastAPI()
#healthy check endpoint
@app.get("/health/")
async def health_check():
    return JSONResponse({"status": "ok"})

@app.post("/heavy_task/")
async def heavy_task(duration: int):
    task = heavy_computation.delay(duration)
    return JSONResponse({"task_id": task.id})

@app.get("/tasks/{task_id}")
async def get_status(task_id: str):
    """Check the status of a specific task."""
    task_result = AsyncResult(task_id)
    
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return JSONResponse(status_code=200, content=result)

#list all tasks with status
@app.get("/list_active_tasks/")
async def list_active_tasks():
    """List all tasks currently running on your workers."""
    # Inspect the live celery cluster state
    inspector = celery_app.control.inspect()
    active_tasks = inspector.active()
    
    if not active_tasks:
        return {"active_tasks": [], "message": "No tasks are currently running."}
        
    formatted_tasks = []
    
    # Celery clusters group active tasks by worker name (e.g., 'celery@Mac')
    for worker_name, tasks in active_tasks.items():
        for task in tasks:
            # Reconstruct an AsyncResult to pull the official status
            task_result = AsyncResult(task["id"], app=celery_app)
            
            formatted_tasks.append({
                "task_id": task["id"],
                "name": task["name"],
                "args": task["args"],
                "kwargs": task["kwargs"],
                "worker": worker_name,
                "status": task_result.status  # Will usually be "STARTED" or "RETRY"
            })
            
    return {"active_tasks": formatted_tasks}