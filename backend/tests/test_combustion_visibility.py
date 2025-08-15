import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import swisseph as swe
from horary_engine.engine import EnhancedTraditionalAstrologicalCalculator
from models import Planet, PlanetPosition, Sign


def _pos(planet, lon, sign):
    return PlanetPosition(planet=planet, longitude=lon, latitude=0.0, house=1, sign=sign, dignity_score=0)


def test_mercury_exception_requires_darkness():
    engine = EnhancedTraditionalAstrologicalCalculator()
    lat = 0.0
    lon = 0.0
    jd_day = swe.julday(2024, 6, 21, 12.0)
    jd_night = swe.julday(2024, 6, 21, 0.0)

    mercury_pos = _pos(Planet.MERCURY, 80.0, Sign.GEMINI)  # 20° Gemini
    sun_pos = _pos(Planet.SUN, 60.0, Sign.GEMINI)  # 0° Gemini

    assert not engine._check_enhanced_combustion_exception(Planet.MERCURY, mercury_pos, sun_pos, lat, lon, jd_day)
    assert engine._check_enhanced_combustion_exception(Planet.MERCURY, mercury_pos, sun_pos, lat, lon, jd_night)


def test_venus_exception_requires_darkness():
    engine = EnhancedTraditionalAstrologicalCalculator()
    lat = 0.0
    lon = 0.0
    jd_day = swe.julday(2024, 6, 21, 12.0)
    jd_night = swe.julday(2024, 6, 21, 0.0)

    venus_pos = _pos(Planet.VENUS, 80.0, Sign.GEMINI)
    sun_pos = _pos(Planet.SUN, 60.0, Sign.GEMINI)

    assert not engine._check_enhanced_combustion_exception(Planet.VENUS, venus_pos, sun_pos, lat, lon, jd_day)
    assert engine._check_enhanced_combustion_exception(Planet.VENUS, venus_pos, sun_pos, lat, lon, jd_night)
