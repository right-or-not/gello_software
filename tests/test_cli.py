"""Software-only checks for the unified command-line dispatcher."""

from gello.cli import COMMANDS, main


def test_top_level_help(capsys):
    assert main(["--help"]) == 0
    output = capsys.readouterr().out
    for command in COMMANDS:
        assert command in output


def test_unknown_command(capsys):
    assert main(["does-not-exist"]) == 2
    assert "unknown command" in capsys.readouterr().err
