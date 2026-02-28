#!/usr/bin/env python3
"""Export the full Agent-Richy codebase into a single text file for review."""

import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "full_codebase_export.txt"

INCLUDE_EXT = {".py", ".json", ".yaml", ".yml", ".md", ".txt", ".env", ".toml", ".cfg"}
SKIP_DIRS = {"node_modules", "__pycache__", ".git", ".venv", "venv", "charts", ".mypy_cache", ".ruff_cache"}
SKIP_EXT = {".pyc", ".duckdb", ".csv"}
MAX_SIZE = 500 * 1024  # 500 KB

SEP = "=" * 80


def dir_tree(root: Path, prefix: str = "", depth: int = 0, max_depth: int = 2) -> list[str]:
    """Return a directory tree list, max_depth levels deep."""
    lines: list[str] = []
    if depth > max_depth:
        return lines
    try:
        entries = sorted(root.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return lines
    dirs = [e for e in entries if e.is_dir() and e.name not in SKIP_DIRS and not e.name.startswith(".")]
    files = [e for e in entries if e.is_file()]
    items = dirs + files
    for i, entry in enumerate(items):
        connector = "├── " if i < len(items) - 1 else "└── "
        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            extension = "│   " if i < len(items) - 1 else "    "
            lines.extend(dir_tree(entry, prefix + extension, depth + 1, max_depth))
        else:
            lines.append(f"{prefix}{connector}{entry.name}")
    return lines


def should_include(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    for p in parts:
        if p in SKIP_DIRS:
            return False
    if path.suffix in SKIP_EXT:
        return False
    if path.suffix not in INCLUDE_EXT:
        return False
    if path.name == OUTPUT.name:
        return False
    try:
        if path.stat().st_size > MAX_SIZE:
            return False
    except OSError:
        return False
    return True


def main():
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune skipped dirs in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        dirnames.sort()
        for fn in sorted(filenames):
            fp = Path(dirpath) / fn
            if should_include(fp):
                files.append(fp)

    total_lines = 0
    with open(OUTPUT, "w", encoding="utf-8") as out:
        # Header
        out.write(f"FULL CODEBASE EXPORT — Agent-Richy\n")
        out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Files: {len(files)}\n")
        out.write(SEP + "\n\n")

        # Directory tree
        out.write("DIRECTORY TREE (2 levels)\n")
        out.write("-" * 40 + "\n")
        out.write(f"{ROOT.name}/\n")
        for line in dir_tree(ROOT):
            out.write(line + "\n")
        out.write("\n" + SEP + "\n\n")

        # File contents
        for fp in files:
            rel = fp.relative_to(ROOT)
            try:
                content = fp.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"[ERROR reading file: {e}]"
            line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
            total_lines += line_count

            out.write(f"FILE: {rel}  ({line_count} lines)\n")
            out.write("-" * 40 + "\n")
            out.write(content)
            if content and not content.endswith("\n"):
                out.write("\n")
            out.write(SEP + "\n\n")

        # Summary
        out.write("SUMMARY\n")
        out.write("-" * 40 + "\n")
        out.write(f"Total files exported: {len(files)}\n")
        out.write(f"Total lines: {total_lines}\n")
        out.write(f"Output: {OUTPUT.name}\n")

    print(f"Exported {len(files)} files ({total_lines} lines) → {OUTPUT.name}")


if __name__ == "__main__":
    main()
