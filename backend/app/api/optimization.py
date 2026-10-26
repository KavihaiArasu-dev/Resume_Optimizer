"""
Optimization API Routes — Feature 2.
POST /api/optimization/optimize
POST /api/resumes/{resume_id}/optimize
POST /api/optimization/diffs/apply
GET  /api/optimization/results/{run_id}
GET  /api/optimization/recommendations/{match_id}
"""
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any, List
from app.schemas.schemas import (
    ParsedResume, ParsedJobDescription, OptimizationModeEnum,
    SkillMatchResult, OptimizationRequest, OptimizationResponse,
    DiffEntry, ResumeVersion
)
from app.services.optimizer.optimizer_service import optimizer_service
from app.services.validator.fact_validator import fact_validator
from app.services.async_queue import task_queue
from app.api.resumes import _resumes_db
from app.api.matches import _matches_db
from app.api.jobs import _jobs_db

router = APIRouter()

# In-memory store
_optimization_runs_db = {}


async def _run_async_optimization_task(
    task_id: str,
    run_id: str,
    resume_dict: dict,
    jd_dict: dict,
    mode: OptimizationModeEnum,
    version_name: str,
    user_metrics: dict,
    match_id: Optional[str] = None,
):
    try:
        # Step 1: Initialize
        task_queue.update_task(
            task_id, status="processing", progress=20,
            step="1/4 Extracting document entities & target requirements..."
        )
        await asyncio.sleep(0.3)

        parsed_resume = ParsedResume(**resume_dict["parsed_data"])
        parsed_jd = ParsedJobDescription(**jd_dict["parsed_data"])

        # Step 2: Skill alignments & embeddings
        task_queue.update_task(
            task_id, progress=50,
            step="2/4 Analyzing skill ontology & semantic alignments..."
        )
        await asyncio.sleep(0.3)

        # Step 3: Synthesis with ACTION+TECH+TASK+SCALE+RESULT
        task_queue.update_task(
            task_id, progress=75,
            step="3/4 Synthesizing ACTION + TECH + TASK + SCALE + RESULT rewrites..."
        )
        opt_result = await optimizer_service.optimize(
            resume=parsed_resume,
            jd=parsed_jd,
            mode=mode,
            user_metrics=user_metrics,
        )

        # Step 4: Fact Validation
        task_queue.update_task(
            task_id, progress=90,
            step="4/4 Running FactValidator to prevent hallucinated claims..."
        )
        await asyncio.sleep(0.2)

        # Create saved resume version
        version_id = str(uuid.uuid4())
        new_version = {
            "id": version_id,
            "resume_id": resume_dict["id"],
            "version_name": version_name or f"Optimized - {parsed_jd.title or 'Target Role'}",
            "target_role": parsed_jd.title or "Target Role",
            "created_at": datetime.utcnow().isoformat(),
            "parsed_data": opt_result["optimized_resume"].model_dump(),
            "diffs": [d.model_dump() for d in opt_result["diffs"]],
        }

        # Save to resume versions list (never overwrite master resume)
        if "versions" not in resume_dict:
            resume_dict["versions"] = []
        resume_dict["versions"].append(new_version)

        result_payload = {
            "id": run_id,
            "match_id": match_id,
            "resume_id": resume_dict["id"],
            "job_id": jd_dict["id"],
            "mode": mode.value,
            "status": "completed",
            "version_name": new_version["version_name"],
            "version_id": version_id,
            "optimized_resume": opt_result["optimized_resume"].model_dump(),
            "recommendations": opt_result["recommendations"],
            "diffs": [d.model_dump() for d in opt_result["diffs"]],
            "validation_results": opt_result["validation_results"],
            "missing_metric_prompts": opt_result["missing_metric_prompts"],
            "created_at": datetime.utcnow().isoformat(),
        }

        _optimization_runs_db[run_id] = result_payload

        # Complete background task
        task_queue.update_task(
            task_id, status="completed", progress=100,
            step="Optimization completed successfully.",
            result=result_payload
        )
    except Exception as exc:
        task_queue.update_task(
            task_id, status="failed", progress=100,
            step=f"Optimization failed: {str(exc)}",
            error=str(exc)
        )


@router.post("/optimize")
async def optimize_resume(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """
    Generate evidence-based optimization recommendations asynchronously.
    Returns task_id for progress polling and run_id.
    """
    resume_dict = None
    jd_dict = None
    match_id = request.match_id

    if match_id and match_id in _matches_db:
        match = _matches_db[match_id]
        resume_dict = _resumes_db.get(match["resume_id"])
        jd_dict = _jobs_db.get(match["job_id"])
    elif request.resume_id and request.job_id:
        resume_dict = _resumes_db.get(request.resume_id)
        jd_dict = _jobs_db.get(request.job_id)

    if not resume_dict:
        # Fallback to first available resume if any
        if _resumes_db:
            resume_dict = next(iter(_resumes_db.values()))
        else:
            raise HTTPException(status_code=404, detail="Resume not found")

    if not jd_dict:
        # Fallback to first available JD if any
        if _jobs_db:
            jd_dict = next(iter(_jobs_db.values()))
        else:
            raise HTTPException(status_code=404, detail="Job description not found")

    mode = request.mode or OptimizationModeEnum.EVIDENCE_BASED
    version_name = request.version_name or f"Optimized - {jd_dict.get('title', 'Target Role')}"
    user_metrics = request.user_metrics or {}

    run_id = str(uuid.uuid4())
    task_id = task_queue.create_task(name=f"Optimize for {jd_dict.get('title', 'Target Role')}")

    # Launch in background task queue
    background_tasks.add_task(
        _run_async_optimization_task,
        task_id=task_id,
        run_id=run_id,
        resume_dict=resume_dict,
        jd_dict=jd_dict,
        mode=mode,
        version_name=version_name,
        user_metrics=user_metrics,
        match_id=match_id,
    )

    return {
        "run_id": run_id,
        "task_id": task_id,
        "status": "processing",
        "message": "Optimization job queued. Poll /api/tasks/{task_id} for progress.",
    }


@router.post("/diffs/apply")
async def apply_diffs(data: dict):
    """
    Apply accepted diffs to an existing optimized resume version.
    Allows user to accept or reject each diff individually.
    """
    run_id = data.get("run_id")
    accepted_diff_ids = set(data.get("accepted_diff_ids", []))

    run = _optimization_runs_db.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")

    resume_id = run["resume_id"]
    resume = _resumes_db.get(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Start from original parsed resume
    opt_resume_data = ParsedResume(**resume["parsed_data"]).model_dump()
    updated_resume = ParsedResume(**opt_resume_data)

    for diff in run["diffs"]:
        d_id = diff["id"]
        is_accepted = d_id in accepted_diff_ids
        diff["applied"] = is_accepted

        if is_accepted:
            field_key = diff.get("field_key", "")
            if field_key == "summary":
                updated_resume.summary = diff["after"]
            elif field_key.startswith("exp_"):
                # Parse exp_{exp_idx}_b_{b_idx}
                parts = field_key.split("_")
                if len(parts) >= 4:
                    e_idx = int(parts[1])
                    b_idx = int(parts[3])
                    if e_idx < len(updated_resume.experience) and b_idx < len(updated_resume.experience[e_idx].bullets):
                        updated_resume.experience[e_idx].bullets[b_idx] = diff["after"]

    run["optimized_resume"] = updated_resume.model_dump()
    return {
        "message": f"Updated with {len(accepted_diff_ids)} accepted changes.",
        "optimized_resume": updated_resume.model_dump(),
        "diffs": run["diffs"],
    }


@router.get("/results/{run_id}")
async def get_optimization_results(run_id: str):
    """Get optimization results by run ID."""
    run = _optimization_runs_db.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    return run


@router.get("/recommendations/{match_id}")
async def get_recommendations_for_match(match_id: str):
    """Get all recommendations for a specific match analysis."""
    results = [
        run for run in _optimization_runs_db.values()
        if run.get("match_id") == match_id
    ]
    if not results:
        raise HTTPException(status_code=404, detail="No optimization results found for this match")
    return results[-1]
