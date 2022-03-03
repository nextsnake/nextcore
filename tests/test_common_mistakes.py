from __future__ import annotations

from pathlib import Path
from ast import parse, ImportFrom, Import

from typing import Any

def test_bad_typings():
    source_path = Path("nextcore/")
    failures = 0

    for path in source_path.rglob("*.py"):
        with open(path) as f:
            file_contents = f.read()

            ast = parse(file_contents, filename=str(path))
            nodes = flatten_ast(ast)

            for node in nodes:
                if not isinstance(node, ImportFrom):
                    continue
                if not node.module == "typing":
                    continue

                for name in node.names:
                    if name.name in ("List", "Dict", "Tuple", "Union", "Optional"):
                        if name.name == "Optional":
                            replacement = "<type> | None"
                        elif name.name == "Union":
                            replacement = "<type> | <type>"
                        else:
                            replacement = name.name.lower()
                        print(f"{path} has a typing import of {name.name}. Please use {replacement} instead. (Note: This requires from __future__ import annotations)")
                        failures += 1
    assert failures == 0, f"{failures} bad typings found"

def test_using_get_event_loop():
    source_path = Path("nextcore/")
    failures = 0

    for path in source_path.rglob("*.py"):
        with open(path) as f:
            file_contents = f.read()

            ast = parse(file_contents, filename=str(path))
            nodes = flatten_ast(ast)

            for node in nodes:
                if isinstance(node, ImportFrom):
                    if not node.module == "asyncio":
                        continue

                    for name in node.names:
                        if name.name == "get_event_loop":
                            print(f"{path} uses get_event_loop. Please use get_running_loop instead.")
                            failures += 1
    assert failures == 0, f"{failures} uses of get_event_loop found"

def test_use_relative_imports():
    source_path = Path("nextcore/")
    failures = 0

    for path in source_path.rglob("*.py"):
        with open(path) as f:
            file_contents = f.read()

            ast = parse(file_contents, filename=str(path))
            nodes = flatten_ast(ast)

            for node in nodes:
                if not isinstance(node, Import):
                    continue
                for name in node.names:
                    print(f"{path} uses non-relative imports for {name.name}. Please use relative imports instead.")
                    failures += 1
    assert failures == 0, f"{failures} uses of relative imports found"



def flatten_ast(ast: Any) -> list[Any]:
    nodes: list[Any] = []
    for node in ast.body:
        nodes.append(node)
        if hasattr(node, "body"):
            nodes.extend(flatten_ast(node))
    return nodes
