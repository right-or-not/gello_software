"""Compatibility wrapper for ``gello read``."""

from gello.commands.read import main

if __name__ == "__main__":
    raise SystemExit(main())
