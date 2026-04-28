from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parent


def module_exists(module: str) -> bool:
    if module.split(".")[0] in {"tkinter","ttk","json","os","sys","sqlite3","datetime","pathlib","subprocess","socket","webbrowser","ast","random","html","ipaddress","re","urllib","io","base64","platform","textwrap"}:
        return True
    parts = module.split(".")
    candidate = ROOT.joinpath(*parts)
    return candidate.with_suffix(".py").exists() or candidate.joinpath("__init__.py").exists()


def check_file(path: Path) -> list[str]:
    errors = []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            mod = node.module
            if mod.startswith("."):
                continue
            if mod.startswith("tkinter"):
                continue
            if mod in {"typing", "__future__"}:
                continue
            if mod in {"pandas", "streamlit", "plotly.express", "requests", "dotenv", "openai"}:
                continue
            if not module_exists(mod):
                errors.append(f"{path}: módulo não encontrado: from {mod} import ...")
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                if mod.split(".")[0] in {"pandas", "streamlit", "plotly", "requests", "dotenv", "tkinter", "openai"}:
                    continue
                if not module_exists(mod):
                    errors.append(f"{path}: módulo não encontrado: import {mod}")
    return errors


def main() -> int:
    errors = []
    for py in ROOT.rglob("*.py"):
        if ".venv" in py.parts:
            continue
        errors.extend(check_file(py))
    if errors:
        print("\n".join(errors))
        return 1
    print("check_project.py: sem erros reais de import.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
