import os
import sys
import datetime
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import (
    Aspect,
    AspectInfo,
    HoraryChart,
    Planet,
    PlanetPosition,
    Sign,
)


def make_chart(hard_aspect: Aspect) -> HoraryChart:
    now = datetime.datetime.utcnow()
    planets = {
        Planet.VENUS: PlanetPosition(Planet.VENUS, 0, 0, 1, Sign.ARIES, 0, speed=1),
        Planet.MARS: PlanetPosition(Planet.MARS, 0, 0, 7, Sign.LIBRA, 0, speed=1),
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 2, Sign.TAURUS, 0, speed=2),
    }
    aspects = [
        AspectInfo(
            planet1=Planet.MERCURY,
            planet2=Planet.VENUS,
            aspect=hard_aspect,
            orb=5,
            applying=False,
        ),
        AspectInfo(
            planet1=Planet.MERCURY,
            planet2=Planet.MARS,
            aspect=Aspect.TRINE,
            orb=5,
            applying=True,
        ),
    ]
    houses = [i * 30 for i in range(12)]
    house_rulers = {1: Planet.VENUS, 7: Planet.MARS}
    return HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=aspects,
        houses=houses,
        house_rulers=house_rulers,
        ascendant=0.0,
        midheaven=0.0,
    )


@pytest.mark.parametrize("hard_aspect", [Aspect.SQUARE, Aspect.OPPOSITION])
def test_translation_with_hard_aspect_unfavorable(monkeypatch, hard_aspect):
    engine = EnhancedTraditionalHoraryJudgmentEngine()

    monkeypatch.setattr(engine, "_is_aspect_within_orb_limits", lambda chart, aspect: True)
    monkeypatch.setattr(
        engine, "_validate_translation_sequence_timing", lambda chart, t, sep, app: True
    )
    monkeypatch.setattr(
        engine, "_check_intervening_aspects", lambda chart, t, sep, app: []
    )

    class DummyReception:
        @staticmethod
        def calculate_comprehensive_reception(chart, planet, target):
            return {"type": "none", "display_text": ""}

    engine.reception_calculator = DummyReception()

    chart = make_chart(hard_aspect)
    result = engine._check_enhanced_translation_of_light(chart, Planet.VENUS, Planet.MARS)

    assert result["found"]
    assert not result["favorable"]
    assert result["confidence"] == 60
