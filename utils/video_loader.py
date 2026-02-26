"""Auto-detection system for video files.

Searches local directories and external URL configs to find the best
video source for each lesson. Supports three delivery methods:

1. **Local file** — MP4 dropped into ``videos/shows/``
2. **External URL** — YouTube or hosted URL in ``videos/video_urls.json``
3. **Placeholder** — graceful "Coming Soon" fallback
"""

import json
import os
import glob
from datetime import datetime
from typing import Optional

# ── Possible directories containing video files ─────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIDEO_DIRECTORIES = [
    os.path.join(_ROOT, "videos", "shows"),       # Primary: repo root
    "videos/shows/",                               # CWD-relative
    "./videos/shows/",                             # Explicit relative
]

VIDEO_URLS_FILE = os.path.join(_ROOT, "videos", "video_urls.json")


# ── Helpers ──────────────────────────────────────────────────────────────

def find_video_file(filename: str) -> Optional[str]:
    """Search known directories for *filename*. Returns absolute path or ``None``."""
    if not filename:
        return None
    for directory in VIDEO_DIRECTORIES:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            return os.path.abspath(filepath)
    return None


def load_video_urls() -> dict[str, str]:
    """Load the external-URL mapping from ``videos/video_urls.json``.

    Returns ``{filename: url}`` (empty dict if the file is missing or invalid).
    """
    if os.path.exists(VIDEO_URLS_FILE):
        try:
            with open(VIDEO_URLS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _is_youtube_url(url: str) -> bool:
    return any(tok in url for tok in ("youtube.com", "youtu.be"))


# ── Primary API ──────────────────────────────────────────────────────────

def get_video_source(show: dict) -> dict:
    """Determine the best video source for a lesson / show dict.

    Priority order:
    1. Local MP4 file in ``videos/shows/``
    2. External URL from ``video_urls.json``
    3. YouTube / external ``video_url`` field already in the data
    4. Placeholder (no video yet)

    Returns::

        {"type": "local_file" | "youtube" | "external_url" | "placeholder",
         "source": <path_or_url_or_None>}
    """
    filename = show.get("video_filename", "") or show.get("show_filename", "")

    # Priority 1: local file on disk
    if filename:
        local_path = find_video_file(filename)
        if local_path:
            return {"type": "local_file", "source": local_path}

    # Priority 2: external URL from video_urls.json
    if filename:
        urls = load_video_urls()
        ext_url = urls.get(filename, "")
        if ext_url:
            if _is_youtube_url(ext_url):
                return {"type": "youtube", "source": ext_url}
            return {"type": "external_url", "source": ext_url}

    # Priority 3: existing video_url field (non-placeholder)
    video_url = show.get("video_url", "")
    if video_url and "PLACEHOLDER" not in video_url.upper() and video_url.startswith("http"):
        if _is_youtube_url(video_url):
            return {"type": "youtube", "source": video_url}
        return {"type": "external_url", "source": video_url}

    # Priority 4: nothing available
    return {"type": "placeholder", "source": None}


def get_all_available_videos() -> dict[str, str]:
    """Scan every known video directory and return ``{filename: abs_path}`` for all ``.mp4`` files."""
    available: dict[str, str] = {}
    for directory in VIDEO_DIRECTORIES:
        if os.path.isdir(directory):
            for filepath in glob.glob(os.path.join(directory, "*.mp4")):
                fname = os.path.basename(filepath)
                if fname not in available:
                    available[fname] = os.path.abspath(filepath)
    return available


# ── Status / Admin helpers ───────────────────────────────────────────────

def get_video_status(show: dict) -> dict:
    """Return a rich status dict for a single lesson / show.

    Keys: ``status`` (str), ``icon`` (str emoji), ``detail`` (str),
    ``file_size`` (int | None), ``last_modified`` (str | None).
    """
    source = get_video_source(show)
    filename = show.get("video_filename", "") or show.get("show_filename", "")
    result = {
        "status": source["type"],
        "icon": "⏳",
        "detail": "Coming Soon",
        "file_size": None,
        "last_modified": None,
        "filename": filename,
    }

    if source["type"] == "local_file":
        result["icon"] = "✅"
        result["detail"] = f"Local: {os.path.basename(source['source'])}"
        try:
            stat = os.stat(source["source"])
            result["file_size"] = stat.st_size
            result["last_modified"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        except OSError:
            pass
    elif source["type"] == "youtube":
        result["icon"] = "🔗"
        result["detail"] = f"YouTube: {source['source']}"
    elif source["type"] == "external_url":
        result["icon"] = "🔗"
        result["detail"] = f"URL: {source['source']}"

    return result


def get_pipeline_summary() -> dict:
    """Return an overview dict suitable for an admin dashboard.

    Keys: ``total_lessons``, ``local_count``, ``youtube_count``,
    ``external_count``, ``placeholder_count``, ``lessons`` (list of status dicts).
    """
    from video_data import VIDEO_MODULES  # local import to avoid circular dep

    lessons_status: list[dict] = []
    counts = {"local_file": 0, "youtube": 0, "external_url": 0, "placeholder": 0}

    for module in VIDEO_MODULES:
        for lesson in module.get("lessons", []):
            status = get_video_status(lesson)
            status["module"] = module["title"]
            status["title"] = lesson.get("title", "")
            status["lesson_id"] = lesson.get("lesson_id", "")
            lessons_status.append(status)
            counts[status["status"]] = counts.get(status["status"], 0) + 1

    return {
        "total_lessons": len(lessons_status),
        "local_count": counts.get("local_file", 0),
        "youtube_count": counts.get("youtube", 0),
        "external_count": counts.get("external_url", 0),
        "placeholder_count": counts.get("placeholder", 0),
        "lessons": lessons_status,
    }
