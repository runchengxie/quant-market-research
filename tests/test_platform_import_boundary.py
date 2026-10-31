"""Production callers use public platform owners; legacy imports stay compatible."""

import ast
from pathlib import Path


def test_production_uses_public_platform_imports():
    root = Path(__file__).resolve().parents[1]
    violations = []
    for directory in (root / "src", root / "scripts"):
        for path in directory.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                elif isinstance(node, ast.Import):
                    names = [item.name for item in node.names]
                elif isinstance(node, ast.Call) and node.args:
                    function = node.func
                    dynamic_import = (
                        isinstance(function, ast.Name) and function.id == "__import__"
                    ) or (isinstance(function, ast.Attribute) and function.attr == "import_module")
                    argument = node.args[0]
                    if isinstance(argument, ast.JoinedStr) and argument.values:
                        argument = argument.values[0]
                    names = (
                        [argument.value]
                        if dynamic_import
                        and isinstance(argument, ast.Constant)
                        and isinstance(argument.value, str)
                        else []
                    )
                else:
                    names = []
                if any(
                    name == "portfolio_backtester" or name.startswith("portfolio_backtester.")
                    for name in names
                ):
                    violations.append(f"{path.relative_to(root)}:{node.lineno}")
    assert not violations, "Legacy production imports: " + ", ".join(violations)
