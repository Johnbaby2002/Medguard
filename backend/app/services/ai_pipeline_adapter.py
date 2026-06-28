from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable

from app.config import settings
from app.schemas import MEDICAL_DISCLAIMER

PIPELINE_FUNCTION_NAMES = ("answer_question", "ask", "analyze", "run", "process")


def _configured_path() -> Path | None:
    if not settings.ai_pipeline_path:
        return None
    path = Path(settings.ai_pipeline_path)
    if not path.is_absolute():
        cwd_candidate = (Path.cwd() / path).resolve()
        backend_candidate = (Path(__file__).resolve().parents[2] / path).resolve()
        project_candidate = (Path(__file__).resolve().parents[3] / path).resolve()
        if cwd_candidate.exists():
            path = cwd_candidate
        elif backend_candidate.exists():
            path = backend_candidate
        else:
            path = project_candidate
    return path.resolve()


def _load_module() -> Any | None:
    if not settings.ai_pipeline_enabled:
        return None

    path = _configured_path()
    if path and path.exists():
        if path.is_file() and path.suffix == ".py":
            module_name = settings.ai_pipeline_module or path.stem
            spec = importlib.util.spec_from_file_location(module_name, path)
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))

    if settings.ai_pipeline_module:
        return importlib.import_module(settings.ai_pipeline_module)
    return None


def _find_pipeline_function(module: Any) -> tuple[str, Callable[..., Any]] | None:
    for function_name in PIPELINE_FUNCTION_NAMES:
        function = getattr(module, function_name, None)
        if callable(function):
            return function_name, function
    return None


def _call_pipeline(function: Callable[..., Any], question: str, snapshot: dict[str, Any]) -> Any:
    attempts = (
        lambda: function(question=question, snapshot=snapshot),
        lambda: function(question, snapshot),
        lambda: function(snapshot),
    )
    last_error: TypeError | None = None
    for attempt in attempts:
        try:
            return attempt()
        except TypeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return None


def _normalize_result(result: Any) -> dict[str, Any]:
    if isinstance(result, str):
        return {"answer": result}
    if isinstance(result, dict):
        normalized = dict(result)
    else:
        normalized = {"answer": str(result)}

    normalized.setdefault("disclaimer", MEDICAL_DISCLAIMER)
    return normalized


def ask_local_ai_pipeline(question: str, snapshot: dict[str, Any]) -> dict[str, Any] | None:
    module = _load_module()
    if module is None:
        return None

    pipeline_function = _find_pipeline_function(module)
    if pipeline_function is None:
        return {
            "error": "Configured AI pipeline module does not expose answer_question, ask, analyze, run, or process."
        }

    function_name, function = pipeline_function
    try:
        result = _call_pipeline(function, question, snapshot)
    except Exception as exc:
        return {"error": f"AI pipeline failed in {function_name}: {exc}"}

    normalized = _normalize_result(result)
    normalized["source"] = f"local_ai_pipeline.{function_name}"
    return normalized


def get_ai_pipeline_status() -> dict[str, Any]:
    path = _configured_path()
    status: dict[str, Any] = {
        "enabled": settings.ai_pipeline_enabled,
        "configured": bool(settings.ai_pipeline_module or settings.ai_pipeline_path),
        "module": settings.ai_pipeline_module,
        "path": str(path) if path else None,
        "connected": False,
        "available_functions": [],
        "message": "No local AI pipeline is configured. Rule-based assistant fallback is active.",
    }

    try:
        module = _load_module()
    except Exception as exc:
        status["message"] = f"AI pipeline could not be loaded: {exc}"
        return status

    if module is None:
        return status

    available = [name for name in PIPELINE_FUNCTION_NAMES if callable(getattr(module, name, None))]
    status["available_functions"] = available
    status["connected"] = bool(available)
    status["message"] = (
        "Local AI pipeline is connected."
        if available
        else "AI pipeline module loaded, but no supported function was found."
    )
    return status
