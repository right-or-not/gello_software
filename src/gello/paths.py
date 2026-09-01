"""Resolve checkout-only assets independently of the package location."""

from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    configured = os.environ.get("GELLO_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "pyproject.toml").is_file():
        return checkout
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file() and (cwd / "src" / "gello").is_dir():
        return cwd
    raise RuntimeError(
        "Cannot locate GELLO; set GELLO_PROJECT_ROOT to its repository root."
    )


def menagerie_root() -> Path:
    configured = os.environ.get("GELLO_MENAGERIE_ROOT")
    root = (
        Path(configured).expanduser().resolve()
        if configured
        else project_root() / "third_party" / "mujoco_menagerie"
    )
    if not root.is_dir():
        raise FileNotFoundError(
            f"MuJoCo Menagerie was not found at {root}. Run "
            "`git submodule update --init --recursive` or set GELLO_MENAGERIE_ROOT."
        )
    return root
