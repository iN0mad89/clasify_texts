from __future__ import annotations

import sys
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional


class Typer:
    def __init__(self, help: str | None = None) -> None:
        self.help = help
        self.commands: Dict[str, Callable[..., Any]] = {}

    def command(self, name: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cmd = name or func.__name__
            self.commands[cmd] = func
            return func

        return decorator

    def __call__(self, args: Optional[List[str]] = None) -> Any:
        if args is None:
            args = sys.argv[1:]
        if not args:
            print(self.help or "Commands: " + ", ".join(self.commands))
            return
        cmd = args[0]
        func = self.commands.get(cmd)
        if func is None:
            print(self.help or f"Unknown command {cmd}")
            return
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        values: Dict[str, Any] = {}
        extras: Dict[str, Any] = {}
        remaining = list(args[1:])
        # parse options first
        i = 0
        while i < len(remaining):
            arg = remaining[i]
            if arg.startswith("--"):
                name = arg[2:].replace("-", "_")
                param = sig.parameters.get(name) or sig.parameters.get(f"{name}_")
                if param and (param.annotation is bool or isinstance(param.default, bool)):
                    extras[param.name] = True
                    i += 1
                elif i == len(remaining) - 1 or remaining[i + 1].startswith("--"):
                    extras[param.name if param else name] = True
                    i += 1
                else:
                    extras[param.name if param else name] = remaining[i + 1]
                    i += 2
            else:
                i += 1
        # collect positional arguments
        positional = [a for a in remaining if not a.startswith("--")]
        pos_iter = iter(positional)
        for p in params:
            if p.kind != p.POSITIONAL_OR_KEYWORD:
                continue
            if p.name in extras:
                val = extras[p.name]
            else:
                try:
                    val = next(pos_iter)
                except StopIteration:
                    val = p.default
            if val is p.empty:
                raise TypeError(f"Missing argument: {p.name}")
            ann = p.annotation
            if isinstance(ann, str):
                ann = eval(ann, func.__globals__)
            if ann is Path:
                val = Path(val)
            elif ann is bool:
                val = bool(val)
            values[p.name] = val
        values.update(extras)
        return func(**values)


def Option(default: Any, *_, **__) -> Any:  # pragma: no cover - simplified
    return default


class Result(SimpleNamespace):
    pass


class CliRunner:
    def invoke(self, app: Typer, args: List[str]) -> Result:
        from io import StringIO

        old_stdout = sys.stdout
        buf = StringIO()
        sys.stdout = buf
        try:
            app(args)
        except SystemExit as e:  # pragma: no cover - emulate click behaviour
            code = e.code
        else:
            code = 0
        finally:
            sys.stdout = old_stdout
        return Result(stdout=buf.getvalue(), exit_code=code)


testing = SimpleNamespace(CliRunner=CliRunner)


def echo(message: Any) -> None:  # pragma: no cover - simple stdout echo
    print(message)
