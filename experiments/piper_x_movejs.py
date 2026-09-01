"""Compatibility wrapper for ``gello movejs``."""

from gello.commands.movejs import main

if __name__ == "__main__":
    raise SystemExit(main())
