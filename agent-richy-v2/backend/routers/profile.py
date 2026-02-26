"""Profile router — /api/profile CRUD."""

from fastapi import APIRouter, HTTPException
from models.profile import FinancialProfile, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])

# In-memory profiles (swap for SQLite/Postgres later)
_profiles: dict[str, FinancialProfile] = {}


@router.get("/{session_id}", response_model=FinancialProfile)
async def get_profile(session_id: str):
    if session_id not in _profiles:
        _profiles[session_id] = FinancialProfile(id=session_id)
    return _profiles[session_id]


@router.put("/{session_id}", response_model=FinancialProfile)
async def update_profile(session_id: str, update: ProfileUpdate):
    if session_id not in _profiles:
        _profiles[session_id] = FinancialProfile(id=session_id)

    profile = _profiles[session_id]
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(profile, key, value)

    return profile


@router.delete("/{session_id}")
async def delete_profile(session_id: str):
    if session_id in _profiles:
        del _profiles[session_id]
    return {"status": "deleted"}
