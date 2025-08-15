import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_config import cfg
from horary_engine import engine as engine_module
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import HoraryChart, Planet, Sign, PlanetPosition


def make_chart():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 1, Sign.ARIES, 0),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 0, 0, 7, Sign.LIBRA, 0),
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 3, Sign.GEMINI, 0),
        Planet.SUN: PlanetPosition(Planet.SUN, 0, 0, 4, Sign.CANCER, 0),
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


def patch_engine(engine, monkeypatch):
    def fake_identify_significators(chart, qa):
        return {
            "valid": True,
            "querent": Planet.MERCURY,
            "quesited": Planet.JUPITER,
            "description": "Mercury-Jupiter",
        }

    monkeypatch.setattr(engine, "_identify_significators", fake_identify_significators)
    monkeypatch.setattr(engine, "_analyze_enhanced_solar_factors", lambda *a, **k: {"significant": False})
    monkeypatch.setattr(
        engine,
        "_check_enhanced_perfection",
        lambda *a, **k: {
            "perfects": True,
            "favorable": False,
            "confidence": cfg().confidence.perfection.direct_basic - 25,
            "type": "direct_penalized",
            "reason": "test penalty",
            "reception": "none",
        },
    )
    monkeypatch.setattr(engine, "_apply_aspect_direction_adjustment", lambda c, p, r: c)
    monkeypatch.setattr(engine, "_apply_dignity_confidence_adjustment", lambda c, ch, q, qs, r: c)
    monkeypatch.setattr(engine, "_apply_retrograde_quesited_penalty", lambda c, ch, q, r: c)
    monkeypatch.setattr(engine, "_apply_confidence_threshold", lambda res, conf, reasoning: (res, conf))
    monkeypatch.setattr(engine, "_calculate_enhanced_timing", lambda *a, **k: None)
    monkeypatch.setattr(engine, "_check_traditional_prohibition", lambda *a, **k: {"found": False})
    monkeypatch.setattr(engine, "_check_moon_sun_education_perfection", lambda *a, **k: {"perfects": False})
    monkeypatch.setattr(engine_module, "check_enhanced_radicality", lambda c, ignore=False: {"valid": True, "reason": "radical"})
    monkeypatch.setattr(engine, "_is_moon_void_of_course_enhanced", lambda c: {"void": False, "exception": False, "reason": ""})


def test_direct_penalized_results_in_no(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    patch_engine(engine, monkeypatch)

    chart = make_chart()
    result = engine._apply_enhanced_judgment(chart, {})

    assert result["result"] == "NO"
    assert result["confidence"] == cfg().confidence.perfection.direct_basic - 25
    assert any("penalized" in r for r in result["reasoning"])

