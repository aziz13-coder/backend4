import os
import sys
import datetime

# Allow importing modules from backend package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import Planet, PlanetPosition, Sign, Aspect, AspectInfo, HoraryChart


def _pos(planet, lon, sign, house):
    return PlanetPosition(
        planet=planet,
        longitude=lon,
        latitude=0.0,
        house=house,
        sign=sign,
        dignity_score=0,
        retrograde=False,
        speed=1.0,
    )


def test_sun_aspect_not_double_scored():
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    now = datetime.datetime(2024, 1, 1)

    planets = {
        Planet.SUN: _pos(Planet.SUN, 0.0, Sign.ARIES, 1),
        Planet.MERCURY: _pos(Planet.MERCURY, 0.5, Sign.ARIES, 1),
        Planet.JUPITER: _pos(Planet.JUPITER, 180.0, Sign.LIBRA, 7),
        Planet.VENUS: _pos(Planet.VENUS, 240.0, Sign.SAGITTARIUS, 9),
    }

    aspects = [
        AspectInfo(
            planet1=Planet.SUN,
            planet2=Planet.MERCURY,
            aspect=Aspect.CONJUNCTION,
            orb=0.5,
            applying=True,
            degrees_to_exact=0.5,
        )
    ]

    chart = HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=aspects,
        houses=[i * 30.0 for i in range(12)],
        house_rulers={1: Planet.MERCURY, 7: Planet.JUPITER},
        ascendant=0.0,
        midheaven=90.0,
    )

    result = engine._check_benefic_aspects_to_significators(
        chart, Planet.MERCURY, Planet.JUPITER
    )

    assert result["total_score"] == 0
    assert result["aspects"] == []
