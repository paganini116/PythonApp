from unittest.mock import patch

import pytest

from date_spot_cli import cli


def strip_ansi(text):
    for code in (cli.RESET, cli.BOLD, cli.CYAN, cli.GREEN):
        text = text.replace(code, "")
    return text


def test_main_prints_suggestions(capsys):
    with patch(
        "date_spot_cli.cli.Spinner",
    ) as spinner_mock, patch(
        "date_spot_cli.cli.suggest_date_spots",
        return_value=(
            "1. The Noodle House - Great for mixed cravings. Budget: around $40.\n"
            "2. Sunset Tapas - Shareable plates and cozy vibe. Budget: around $70.\n"
            "3. Night Market Eats - Variety and fun atmosphere. Budget: around $55."
        ),
    ):
        exit_code = cli.main(
            [
                "--person1-food",
                "sushi",
                "--person2-food",
                "tacos",
                "--city",
                "Seattle",
                "--budget",
                "120",
            ]
        )

    captured = capsys.readouterr()
    output = strip_ansi(captured.out)

    assert exit_code == 0
    spinner_mock.return_value.start.assert_called_once()
    spinner_mock.return_value.stop.assert_called_once()
    assert "[OK] Found a few date spot ideas." in output
    assert "DATE SPOT SUGGESTIONS" in output
    assert "Seattle" in output
    assert "1. The Noodle House" in output
    assert "3. Night Market Eats" in output


def test_empty_string_argument_fails():
    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "--person1-food",
                " ",
                "--person2-food",
                "tacos",
                "--city",
                "Seattle",
                "--budget",
                "120",
            ]
        )

    assert exc_info.value.code == 2


def test_non_positive_budget_fails():
    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "--person1-food",
                "sushi",
                "--person2-food",
                "tacos",
                "--city",
                "Seattle",
                "--budget",
                "0",
            ]
        )

    assert exc_info.value.code == 2


def test_missing_api_key_exits_with_clear_error(capsys):
    with patch("date_spot_cli.cli.Spinner") as spinner_mock, patch(
        "date_spot_cli.cli.suggest_date_spots",
        side_effect=ValueError("OPENAI_API_KEY is not set in the environment."),
    ):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(
                [
                    "--person1-food",
                    "sushi",
                    "--person2-food",
                    "tacos",
                    "--city",
                    "Seattle",
                    "--budget",
                    "120",
                ]
            )

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    spinner_mock.return_value.start.assert_called_once()
    spinner_mock.return_value.stop.assert_called_once()
    assert "OPENAI_API_KEY is not set" in captured.err
