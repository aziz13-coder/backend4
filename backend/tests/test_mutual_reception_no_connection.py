import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_engine import engine as engine_module
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import HoraryChart, Planet, Sign, PlanetPosition


def make_chart():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 1, Sign.SAGITTARIUS, 0),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 0, 0, 7, Sign.GEMINI, 0),
        Planet.SUN: PlanetPosition(Planet.SUN, 0, 0, 4, Sign.CANCER, 0),
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 3, Sign.ARIES, 0),
    }
    houses = [i * 30 for i in range(12)]
    house_rulers = {1: Planet.MERCURY, 7: Planet.JUPITER}
    return HoraryChart(
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


def test_mutual_reception_without_connection(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    chart = make_chart()

    def fake_identify_significators(chart, qa):
        return {
            "valid": True,
            "querent": Planet.MERCURY,
            "quesited": Planet.JUPITER,
            "description": "Mercury-Jupiter",
        }

    monkeypatch.setattr(engine, "_identify_significators", fake_identify_significators)
    monkeypatch.setattr(
        engine_module,
        "check_enhanced_radicality",
        lambda c, ignore=False: {"valid": True, "reason": "radical"},
    )
    monkeypatch.setattr(
        engine,
        "_is_moon_void_of_course_enhanced",
        lambda c: {"void": False, "exception": False, "reason": ""},
    )
    monkeypatch.setattr(
        engine,
        "_analyze_enhanced_solar_factors",
        lambda *a, **k: {"significant": False},
    )
    monkeypatch.setattr(engine, "_apply_aspect_direction_adjustment", lambda c, p, r: c)
    monkeypatch.setattr(engine, "_apply_dignity_confidence_adjustment", lambda c, ch, q, qs, r: c)
    monkeypatch.setattr(engine, "_apply_retrograde_quesited_penalty", lambda c, ch, q, r: c)
    monkeypatch.setattr(engine, "_calculate_enhanced_timing", lambda *a, **k: None)
    monkeypatch.setattr(engine, "_check_enhanced_moon_testimony", lambda *a, **k: {})
    monkeypatch.setattr(engine, "_check_enhanced_denial_conditions", lambda *a, **k: {"denied": False})
    monkeypatch.setattr(engine, "_check_moon_next_aspect_to_significators", lambda *a, **k: {"decisive": False, "result": "NO", "confidence": 70, "reason": ""})
    monkeypatch.setattr(engine, "_check_benefic_aspects_to_significators", lambda *a, **k: {"favorable": False})

    perfection = engine._check_enhanced_perfection(chart, Planet.MERCURY, Planet.JUPITER)
    assert perfection["reception"] == "mutual_rulership"
    assert not perfection["perfects"]

    result = engine._apply_enhanced_judgment(chart, {})
    assert result["result"] == "NO"

