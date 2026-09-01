"""Compatibility wrapper for ``gello camera-client``."""

import tyro

from gello.commands.camera_client import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
