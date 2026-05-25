#!/usr/bin/env python3
"""轻量 YAML 读写（仅支持本仓库 shots/manifest 结构，无第三方依赖）。"""

from __future__ import annotations

import re
from typing import Any


def _yaml_quote(s: str) -> str:
    if re.match(r"^[\w./:-]+$", s) and " " not in s:
        return s
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dump_yaml(obj: Any, indent: int = 0) -> str:
    sp = "  " * indent
    if isinstance(obj, dict):
        lines: list[str] = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{sp}{k}:")
                lines.append(dump_yaml(v, indent + 1))
            elif isinstance(v, list) and not v:
                lines.append(f"{sp}{k}: []")
            elif isinstance(v, bool):
                lines.append(f"{sp}{k}: {'true' if v else 'false'}")
            elif isinstance(v, (int, float)):
                lines.append(f"{sp}{k}: {v}")
            elif v is None:
                lines.append(f"{sp}{k}: null")
            else:
                lines.append(f"{sp}{k}: {_yaml_quote(str(v))}")
        return "\n".join(lines)
    if isinstance(obj, list):
        lines: list[str] = []
        for item in obj:
            if isinstance(item, dict):
                lines.append(f"{sp}-")
                inner = dump_yaml(item, indent + 1)
                for ln in inner.splitlines():
                    lines.append(ln)
            else:
                lines.append(f"{sp}- {_yaml_quote(str(item))}")
        return "\n".join(lines)
    return f"{sp}{_yaml_quote(str(obj))}"


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in ("true", "True"):
        return True
    if raw in ("false", "False"):
        return False
    if raw in ("null", "~", ""):
        return None
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.match(r"^-?\d+$", raw):
        return int(raw)
    return raw


def load_yaml(text: str) -> Any:
    lines = text.splitlines()
    root: Any = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        if stripped.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"expected list at indent {indent}")
            val = stripped[2:].strip()
            if val:
                parent.append(_parse_scalar(val))
            else:
                item: dict = {}
                parent.append(item)
                stack.append((indent, item))
            i += 1
            continue

        if stripped.startswith("-") and stripped == "-":
            if not isinstance(parent, list):
                raise ValueError(f"expected list at indent {indent}")
            item = {}
            parent.append(item)
            stack.append((indent, item))
            i += 1
            continue

        if ":" not in stripped:
            i += 1
            continue

        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()

        if rest:
            value = _parse_scalar(rest)
            if isinstance(parent, dict):
                parent[key] = value
            else:
                raise ValueError(f"cannot set key on non-dict: {key}")
            i += 1
            continue

        # key with nested block on following lines
        peek = i + 1
        if peek < len(lines):
            nxt = lines[peek]
            nxt_indent = len(nxt) - len(nxt.lstrip(" "))
            if nxt_indent > indent and nxt.strip():
                if nxt.strip().startswith("- "):
                    child: Any = []
                else:
                    child = {}
                if isinstance(parent, dict):
                    parent[key] = child
                else:
                    raise ValueError(f"cannot nest key on non-dict: {key}")
                stack.append((indent, child))
        i += 1

    return root
