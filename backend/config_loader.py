"""
Load and merge config/default.yaml and config/secrets.yaml.
Provides a single merged config and a dotted-path getter.
"""
import logging
import os
from copy import deepcopy
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

_log = logging.getLogger(__name__)

# Lazy-loaded merged config (defaults + secrets overlay)
_config: Optional[dict] = None


def _project_root() -> str:
    """Directory containing the 'config' folder (project root)."""
    this_file = os.path.abspath(__file__)
    backend_dir = os.path.dirname(this_file)
    return os.path.dirname(backend_dir)


def _config_dir() -> str:
    return os.path.join(_project_root(), "config")


def _load_yaml(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    if yaml is None:
        _log.warning("PyYAML not installed; config from %s will be ignored.", path)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        _log.warning("Could not load %s: %s", path, e)
        return {}


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Merge overlay into base recursively. Modifies base in place."""
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = deepcopy(value)
    return base


def _load_config() -> dict:
    global _config
    if _config is not None:
        return _config
    root = _project_root()
    config_dir = os.path.join(root, "config")
    default_path = os.path.join(config_dir, "default.yaml")
    secrets_path = os.path.join(config_dir, "secrets.yaml")

    defaults = _load_yaml(default_path)
    if not defaults and os.path.isfile(default_path):
        defaults = {}
    secrets = _load_yaml(secrets_path)
    merged = deepcopy(defaults)
    _deep_merge(merged, secrets)
    _config = merged
    return _config


def get_config() -> dict:
    """Return the merged config (defaults + secrets). Do not mutate the result."""
    return deepcopy(_load_config())


def get(key_path: str, default: Any = None) -> Any:
    """
    Get a value by dotted path, e.g. get("pdf_utils.dpi") or get("math_recognition.timeout").
    Returns default if the path is missing.
    """
    cfg = _load_config()
    parts = key_path.strip().split(".")
    obj: Any = cfg
    for part in parts:
        if not part or not isinstance(obj, dict) or part not in obj:
            return default
        obj = obj[part]
    return obj


def reload_config() -> None:
    """Force reload of config on next get_config() or get(). Used for tests or hot-reload."""
    global _config
    _config = None
