import json

import pytest

from jeszcze_zdaze.cli import main


def test_cli_is_explicitly_synthetic_and_returns_plans(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    result = json.loads(capsys.readouterr().out)
    assert result["synthetic"] is True
    assert result["notice"].startswith("DEMO")
    assert result["result"]["plans"]
