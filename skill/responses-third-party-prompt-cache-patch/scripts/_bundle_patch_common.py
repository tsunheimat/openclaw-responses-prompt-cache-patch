#!/usr/bin/env python3
"""Shared helpers for the responses third-party prompt-cache patch skill."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

SKILL_SLUG = "responses-third-party-prompt-cache-patch"
PATCH_MARKER = "openclaw-skill:responses-third-party-prompt-cache-patch"
BACKUP_TOKEN = f"bak.{SKILL_SLUG}"
TARGET_FUNCTION_SIGNATURE = "function shouldStripResponsesPromptCache(model) {"
TARGET_RETURN = "return !isDirectOpenAIBaseUrl(model.baseUrl);"
PATCHED_RETURN = f"return false; /* {PATCH_MARKER} */"
PREFERRED_PATTERNS: Sequence[str] = ("pi-embedded-*.js",)
FALLBACK_PATTERNS: Sequence[str] = ("*.js",)


class PatchError(RuntimeError):
    """Raised when the patch workflow cannot continue safely."""


@dataclass
class BundleInspection:
    path: Path
    text: str
    function_start: int
    function_end: int
    function_block: str
    state: str


def resolve_openclaw_root(explicit_root: str | None) -> Path:
    """Resolve the OpenClaw installation root.

    The skill defaults to the currently installed OpenClaw by resolving the
    `openclaw` executable. `--root` can override this for fixtures or other
    installations.
    """

    if explicit_root:
        root = Path(explicit_root).expanduser().resolve()
        ensure_dist_dir(root)
        return root

    executable = shutil.which("openclaw")
    checked: list[Path] = []
    if executable:
        resolved = Path(executable).expanduser().resolve()
        candidates = [
            resolved.parent,
            resolved.parent.parent,
            resolved.parent.parent / "lib" / "node_modules" / "openclaw",
        ]
        for candidate in candidates:
            if candidate in checked:
                continue
            checked.append(candidate)
            if (candidate / "dist").is_dir():
                return candidate

    checked_summary = ", ".join(str(path) for path in checked) if checked else "<none>"
    raise PatchError(
        "Could not locate the installed OpenClaw root automatically. "
        "Pass --root /path/to/openclaw. Checked: "
        f"{checked_summary}"
    )


def ensure_dist_dir(root: Path) -> Path:
    dist_dir = root / "dist"
    if not dist_dir.is_dir():
        raise PatchError(f"Expected dist/ under {root}, but {dist_dir} does not exist")
    return dist_dir


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PatchError(f"Failed to decode {path} as UTF-8: {exc}") from exc
    except OSError as exc:
        raise PatchError(f"Failed to read {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise PatchError(f"Failed to write {path}: {exc}") from exc


def iter_candidate_bundles(dist_dir: Path) -> list[Path]:
    preferred = collect_bundles(dist_dir, PREFERRED_PATTERNS)
    preferred_matches = [path for path in preferred if bundle_contains_target(path)]
    if preferred_matches:
        return preferred_matches

    fallback = collect_bundles(dist_dir, FALLBACK_PATTERNS)
    fallback_matches = [
        path for path in fallback if path not in preferred and bundle_contains_target(path)
    ]
    return fallback_matches


def collect_bundles(dist_dir: Path, patterns: Iterable[str]) -> list[Path]:
    seen: set[Path] = set()
    bundles: list[Path] = []
    for pattern in patterns:
        for path in sorted(dist_dir.glob(pattern)):
            if not path.is_file():
                continue
            if BACKUP_TOKEN in path.name:
                continue
            if path.suffix != ".js":
                continue
            if path in seen:
                continue
            seen.add(path)
            bundles.append(path)
    return bundles


def bundle_contains_target(path: Path) -> bool:
    try:
        return TARGET_FUNCTION_SIGNATURE in read_text(path)
    except PatchError:
        return False


def inspect_bundle(path: Path) -> BundleInspection:
    text = read_text(path)
    function_start, function_end, function_block = locate_target_function(text, path)
    if PATCH_MARKER in function_block:
        state = "patched"
    elif TARGET_RETURN in function_block:
        state = "patchable"
    else:
        state = "unexpected"
    return BundleInspection(
        path=path,
        text=text,
        function_start=function_start,
        function_end=function_end,
        function_block=function_block,
        state=state,
    )


def locate_target_function(text: str, path: Path) -> tuple[int, int, str]:
    start = text.find(TARGET_FUNCTION_SIGNATURE)
    if start < 0:
        raise PatchError(f"Target function not found in {path}")

    brace_start = text.find("{", start)
    if brace_start < 0:
        raise PatchError(f"Malformed target function in {path}: missing opening brace")

    depth = 0
    for index in range(brace_start, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                return start, end, text[start:end]

    raise PatchError(f"Malformed target function in {path}: missing closing brace")


def build_patched_text(inspection: BundleInspection) -> str:
    if inspection.state == "patched":
        return inspection.text
    if inspection.state != "patchable":
        raise PatchError(
            f"Refusing to patch {inspection.path}: target function exists but no longer matches the expected return line"
        )

    patched_block = inspection.function_block.replace(TARGET_RETURN, PATCHED_RETURN, 1)
    if patched_block == inspection.function_block:
        raise PatchError(f"Failed to patch {inspection.path}: return line was not replaced")

    return (
        inspection.text[: inspection.function_start]
        + patched_block
        + inspection.text[inspection.function_end :]
    )


def create_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_name = f"{path.name}.{BACKUP_TOKEN}.{timestamp}"
    backup_path = path.with_name(base_name)
    counter = 1
    while backup_path.exists():
        backup_path = path.with_name(f"{base_name}.{counter}")
        counter += 1
    try:
        shutil.copy2(path, backup_path)
    except OSError as exc:
        raise PatchError(f"Failed to create backup for {path}: {exc}") from exc
    return backup_path


def list_skill_backups(dist_dir: Path) -> list[Path]:
    return sorted(dist_dir.glob(f"*.{BACKUP_TOKEN}.*"))


def list_matching_backups(bundle_path: Path) -> list[Path]:
    return sorted(bundle_path.parent.glob(f"{bundle_path.name}.{BACKUP_TOKEN}.*"))


def latest_matching_backup(bundle_path: Path) -> Path | None:
    backups = list_matching_backups(bundle_path)
    if not backups:
        return None
    return backups[-1]


def run_node_check(path: Path) -> None:
    try:
        result = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise PatchError("node is required but was not found in PATH") from exc

    if result.returncode != 0:
        combined = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
        raise PatchError(f"node --check failed for {path}\n{combined}")


def copy_file(source: Path, destination: Path) -> None:
    try:
        shutil.copy2(source, destination)
    except OSError as exc:
        raise PatchError(f"Failed to copy {source} to {destination}: {exc}") from exc


def format_paths(paths: Iterable[Path]) -> str:
    return ", ".join(str(path) for path in paths)
