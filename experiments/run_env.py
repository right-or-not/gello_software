"""Compatibility wrapper for ``gello run-env``."""

import tyro

from gello.commands.run_env import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
