"""Compatibility wrapper for ``gello camera-server``."""

import tyro

from gello.commands.camera_server import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
