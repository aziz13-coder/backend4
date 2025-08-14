import os
import sys
import datetime

# Allow importing modules from the backend package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from horary_config import cfg
from horary_engine.radicality import check_enhanced_radicality
from models import HoraryChart, Planet, Sign, PlanetPosition


@pytest.mark.parametrize(
    "enabled, matches, expected",
    [
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, True),
    ],
)
def test_planetary_hour_agreement(monkeypatch, enabled, matches, expected):
    config = cfg()
    monkeypatch.setattr(config.radicality, "hour_agreement_enabled", enabled)
    monkeypatch.setattr(config.radicality, "hour_agreement_mode", "ruler")

    base_dt = datetime.datetime(2024, 9, 2, 0, 0)  # Monday
    if matches:
        dt = base_dt  # planetary hour ruler Moon
        asc_sign = Sign.CANCER  # ruler Moon
    else:
        dt = base_dt + datetime.timedelta(hours=1)  # planetary hour ruler Saturn
        asc_sign = Sign.ARIES  # ruler Mars

    asc_degree = asc_sign.value[0] + 10  # 10 degrees into the sign

    planets = {
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 1, Sign.ARIES, 0),
        Planet.SATURN: PlanetPosition(Planet.SATURN, 0, 0, 1, Sign.ARIES, 0),
    }

    chart = HoraryChart(
        date_time=dt,
        date_time_utc=dt,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={i: Planet.MARS for i in range(1, 13)},
        ascendant=asc_degree,
        midheaven=0.0,
    )

    result = check_enhanced_radicality(chart)
    assert result["valid"] is expected
