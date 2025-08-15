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


def make_chart(translator_speed: float, querent_speed: float, quesited_speed: float) -> HoraryChart:
    now = datetime.datetime.utcnow()
    planets = {
        Planet.VENUS: PlanetPosition(Planet.VENUS, 0, 0, 1, Sign.ARIES, 0, speed=querent_speed),
        Planet.MARS: PlanetPosition(Planet.MARS, 0, 0, 7, Sign.LIBRA, 0, speed=quesited_speed),
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 2, Sign.TAURUS, 0, speed=translator_speed),
    }
    aspects = [
        AspectInfo(
            planet1=Planet.MERCURY,
            planet2=Planet.VENUS,
            aspect=Aspect.TRINE,
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


def _setup_engine(monkeypatch) -> EnhancedTraditionalHoraryJudgmentEngine:
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
    return engine


def test_translation_requires_speed_advantage(monkeypatch):
    engine = _setup_engine(monkeypatch)
    chart = make_chart(translator_speed=1, querent_speed=2, quesited_speed=2)

    result = engine._check_enhanced_translation_of_light(chart, Planet.VENUS, Planet.MARS)

    assert not result["found"]


def test_translation_no_reception_sequence_clean(monkeypatch):
    engine = _setup_engine(monkeypatch)
    chart = make_chart(translator_speed=3, querent_speed=1, quesited_speed=2)

    result = engine._check_enhanced_translation_of_light(chart, Planet.VENUS, Planet.MARS)

    assert result["found"]
    assert "with reception" not in result["sequence"]
    assert result["reception"] == "none"

