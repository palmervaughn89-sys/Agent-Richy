"""Kids education router — /api/kids."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from data.video_data import (
    VIDEO_MODULES,
    MODULE_BADGES,
    MEGA_BADGE,
    get_module_by_id,
)

router = APIRouter(prefix="/api/kids", tags=["kids"])

# In-memory progress per session
_progress: dict[str, dict] = {}


class LessonProgress(BaseModel):
    lesson_id: str
    completed: bool = False
    quiz_score: Optional[int] = None
    quiz_total: Optional[int] = None


class ModuleProgress(BaseModel):
    module_id: str
    lessons_completed: list[str] = Field(default_factory=list)
    badge_earned: bool = False


@router.get("/modules")
async def get_modules():
    """Return all kids education modules and lessons."""
    return {
        "modules": VIDEO_MODULES,
        "badges": MODULE_BADGES,
        "mega_badge": MEGA_BADGE,
        "total_lessons": sum(len(m["lessons"]) for m in VIDEO_MODULES),
    }


@router.get("/modules/{module_id}")
async def get_module(module_id: str):
    """Get a specific module by ID."""
    module = get_module_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.get("/progress/{session_id}")
async def get_progress(session_id: str):
    """Get lesson progress for a session."""
    return _progress.get(session_id, {"completed_lessons": [], "badges": [], "quiz_scores": {}})


@router.post("/progress/{session_id}")
async def update_progress(session_id: str, progress: LessonProgress):
    """Update lesson completion / quiz score."""
    if session_id not in _progress:
        _progress[session_id] = {"completed_lessons": [], "badges": [], "quiz_scores": {}}

    p = _progress[session_id]
    if progress.completed and progress.lesson_id not in p["completed_lessons"]:
        p["completed_lessons"].append(progress.lesson_id)

    if progress.quiz_score is not None:
        p["quiz_scores"][progress.lesson_id] = {
            "score": progress.quiz_score,
            "total": progress.quiz_total or 0,
        }

    # Check for badge completion
    for module in VIDEO_MODULES:
        lesson_ids = [l["lesson_id"] for l in module["lessons"]]
        if all(lid in p["completed_lessons"] for lid in lesson_ids):
            badge_id = module["module_id"]
            if badge_id not in p["badges"]:
                p["badges"].append(badge_id)

    return p
