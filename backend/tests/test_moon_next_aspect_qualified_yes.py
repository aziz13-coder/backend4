import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import Planet, Sign, PlanetPosition, HoraryChart, LunarAspect, Aspect


def make_chart_with_moon_next():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 1, Sign.ARIES, 0),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 0, 0, 7, Sign.LIBRA, 0),
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 3, Sign.GEMINI, 0),
    }
    houses = [i * 30 for i in range(12)]
    house_rulers = {1: Planet.MERCURY, 7: Planet.JUPITER}
    chart = HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=houses,
        house_rulers=house_rulers,
        ascendant=0.0,
        midheaven=0.0,
    )
    chart.moon_next_aspect = LunarAspect(
        planet=Planet.JUPITER,
        aspect=Aspect.TRINE,
        orb=1.5,
        degrees_difference=5.0,
        perfection_eta_days=1.0,
        perfection_eta_description="1 day",
        applying=True,
    )
    return chart


def test_moon_next_aspect_confers_qualified_yes(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    chart = make_chart_with_moon_next()

    monkeypatch.setattr(engine, "_is_moon_void_of_course_enhanced", lambda c: {"void": False, "exception": False, "reason": ""})
    monkeypatch.setattr(engine, "_detect_reception_between_planets", lambda *a, **k: "none")

    result = engine._check_moon_next_aspect_to_significators(chart, Planet.MERCURY, Planet.JUPITER)

    assert result["result"] == "YES"
    assert result["decisive"] is True
    # Base 75 confidence +20 applying bonus
    assert result["confidence"] == 95
