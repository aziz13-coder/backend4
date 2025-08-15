import datetime

import pytest

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import (
    Aspect,
    AspectInfo,
    HoraryChart,
    Planet,
    PlanetPosition,
    Sign,
)


def test_later_aspect_does_not_prohibit():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 1, Sign.ARIES, 0, False, 1.0),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 0, 0, 7, Sign.LIBRA, 0, False, 0.5),
        Planet.SATURN: PlanetPosition(Planet.SATURN, 0, 0, 4, Sign.CAPRICORN, 0, False, 0.4),
    }

    direct = AspectInfo(
        planet1=Planet.MERCURY,
        planet2=Planet.JUPITER,
        aspect=Aspect.CONJUNCTION,
        orb=5.0,
        applying=True,
        degrees_to_exact=5.0,
    )

    prohibiting = AspectInfo(
        planet1=Planet.JUPITER,
        planet2=Planet.SATURN,
        aspect=Aspect.CONJUNCTION,
        orb=5.0,
        applying=True,
        degrees_to_exact=4.0,
    )

    chart = HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=[direct, prohibiting],
        houses=[i * 30 for i in range(12)],
        house_rulers={1: Planet.MERCURY, 7: Planet.JUPITER},
        ascendant=0.0,
        midheaven=0.0,
    )

    engine = EnhancedTraditionalHoraryJudgmentEngine()
    engine._check_dignified_reception = lambda *a, **k: False

    result = engine._check_traditional_prohibition(chart, Planet.MERCURY, Planet.JUPITER)
    assert result["found"] is False
