"""Unified command-line interface for GELLO software."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Command:
    module: str
    description: str
    parser: Literal["argparse", "tyro"] = "argparse"
    extra: str | None = None


COMMANDS: dict[str, Command] = {
    "read": Command("gello.commands.read", "read GELLO joints and gripper"),
    "follow": Command("gello.commands.follow", "control PiPER-X with GELLO"),
    "follow-record": Command(
        "gello.commands.follow_record", "control PiPER-X and record raw episodes"
    ),
    "movejs": Command("gello.commands.movejs", "move PiPER-X through its JS channel"),
    "launch-yaml": Command(
        "gello.commands.launch_yaml", "launch from a YAML configuration", "tyro"
    ),
    "launch-nodes": Command(
        "gello.commands.launch_nodes", "launch a robot ZMQ server", "tyro", "robots"
    ),
    "camera-server": Command(
        "gello.commands.camera_server", "serve RealSense cameras", "tyro", "camera"
    ),
    "camera-client": Command(
        "gello.commands.camera_client",
        "display remote camera streams",
        "tyro",
        "camera",
    ),
    "quick-run": Command(
        "gello.commands.quick_run", "run the upstream quick workflow", "tyro", "full"
    ),
    "run-env": Command(
        "gello.commands.run_env", "run a configured GELLO environment", "tyro", "full"
    ),
}


def _print_help() -> None:
    print("usage: gello COMMAND [OPTIONS]\n")
    print("GELLO hardware, teleoperation, and experiment commands.\n")
    print("commands:")
    width = max(len(name) for name in COMMANDS)
    for name, command in COMMANDS.items():
        suffix = f" [extra: {command.extra}]" if command.extra else ""
        print(f"  {name:<{width}}  {command.description}{suffix}")
    print("\nRun `gello COMMAND --help` for command-specific options.")


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        _print_help()
        return 0
    name = args.pop(0)
    command = COMMANDS.get(name)
    if command is None:
        print(f"gello: unknown command: {name!r}", file=sys.stderr)
        _print_help()
        return 2
    try:
        module = importlib.import_module(command.module)
        if command.parser == "tyro":
            import tyro

            parsed = tyro.cli(module.Args, prog=f"gello {name}", args=args)
            result = module.main(parsed)
        else:
            result = module.main(args)
    except ModuleNotFoundError as exc:
        if command.extra:
            print(
                f"gello {name}: missing optional dependency {exc.name!r}; "
                f"run `uv sync --extra {command.extra}`",
                file=sys.stderr,
            )
            return 1
        raise
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
