"""Compatibility wrapper for ``gello launch-nodes``."""

import tyro

from gello.commands.launch_nodes import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
