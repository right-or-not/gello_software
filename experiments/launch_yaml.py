"""Compatibility wrapper for ``gello launch-yaml``."""

import tyro

from gello.commands.launch_yaml import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
