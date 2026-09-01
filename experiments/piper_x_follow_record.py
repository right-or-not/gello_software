"""Compatibility wrapper for ``gello follow-record``."""

from gello.commands.follow_record import _sample_from_cycle, main

__all__ = ["_sample_from_cycle", "main"]
if __name__ == "__main__":
    raise SystemExit(main())
