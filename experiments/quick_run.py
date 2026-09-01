"""Compatibility wrapper for ``gello quick-run``."""

import tyro

from gello.commands.quick_run import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
