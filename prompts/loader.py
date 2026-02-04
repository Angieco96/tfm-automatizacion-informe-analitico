from pathlib import Path
from string import Template
import json

BASE = Path(__file__).resolve().parent

def get_prompt(*path_parts) -> str:
    path = BASE.joinpath(*path_parts)
    return path.read_text(encoding="utf-8")

def render_prompt(template_str: str, **kwargs) -> str:
    safe_kwargs = {
        k: (json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else v)
        for k, v in kwargs.items()
    }
    return Template(template_str).safe_substitute(**safe_kwargs)
