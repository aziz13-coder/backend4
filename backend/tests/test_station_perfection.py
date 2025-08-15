import sys
import os
import datetime

from hypothesis import given, strategies as st, settings, HealthCheck

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import horary_engine.engine as engine_module
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import Planet, Sign, PlanetPosition, HoraryChart


@settings(deadline=None, max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.floats(min_value=0.1, max_value=50.0))
def test_station_after_perfection_does_not_deny(monkeypatch, extra_days):
    """A station after aspect perfection should not cause denial."""

    engine = EnhancedTraditionalHoraryJudgmentEngine()

    # Simple planet positions with known relative speed
    pos1 = PlanetPosition(
        planet=Planet.MARS,
        longitude=10.0,
        latitude=0.0,
        house=1,
        sign=Sign.ARIES,
        dignity_score=0,
        retrograde=False,
        speed=1.0,
    )
    pos2 = PlanetPosition(
        planet=Planet.VENUS,
        longitude=15.0,
        latitude=0.0,
        house=7,
        sign=Sign.ARIES,
        dignity_score=0,
        retrograde=False,
        speed=0.5,
    )

    aspect_info = {"degrees_to_exact": 5.0}
    days_to_perfect = aspect_info["degrees_to_exact"] / abs(pos1.speed - pos2.speed)

    now = datetime.datetime.utcnow()
    chart = HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets={Planet.MARS: pos1, Planet.VENUS: pos2},
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={1: Planet.MARS, 7: Planet.VENUS},
        ascendant=0.0,
        midheaven=0.0,
        julian_day=0.0,
    )

    def fake_station_time(planet_id, jd_start, max_days=365):
        return jd_start + days_to_perfect + extra_days

    monkeypatch.setattr(engine_module, "calculate_next_station_time", fake_station_time)

    assert engine._enhanced_perfects_in_sign(pos1, pos2, aspect_info, chart)

