"""Compatibility wrapper for ``gello follow``."""

from gello.commands.follow import main

if __name__ == "__main__":
    raise SystemExit(main())
