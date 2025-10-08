from datetime import date

import pytest

from decree.utils import resolve_date


def test_default_uses_local_today() -> None:
    frozen_today = date(2024, 1, 2)
    expected_date = frozen_today.isoformat()
    assert resolve_date(today=lambda: frozen_today) == expected_date


def test_env_override_wins_over_today() -> None:
    env_date = "1999-12-31"
    frozen_today = date(2024, 1, 2)
    expected_date = env_date
    assert resolve_date(env={"ADR_DATE": env_date}, today=lambda: frozen_today) == expected_date


def test_invalid_override_raises() -> None:
    invalid_date = "1999/12/31"
    frozen_today = date(2024, 1, 2)
    with pytest.raises(ValueError) as exc:
        resolve_date(env={"ADR_DATE": invalid_date}, today=lambda: frozen_today)
    assert invalid_date in str(exc.value)
