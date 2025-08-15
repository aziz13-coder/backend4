import os
import sys
import datetime

# Ensure modules in parent directory are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import HoraryChart, Planet, PlanetPosition, Sign
from horary_config import cfg


def make_chart():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 3, Sign.GEMINI, 0),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 10, 0, 9, Sign.AQUARIUS, 0),
        Planet.MOON: PlanetPosition(Planet.MOON, 20, 0, 12, Sign.ARIES, 0),
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
            "perfects": False,
            "favorable": True,
            "confidence": cfg().confidence.perfection.direct_basic - 15,
            "type": "direct",
            "reason": "Trine between significators but weakened",
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
    monkeypatch.setattr(engine, "_is_moon_void_of_course_enhanced", lambda c: {"void": False, "exception": False, "reason": ""})
    monkeypatch.setattr(engine, "_check_moon_next_aspect_to_significators", lambda *a, **k: {"result": "YES", "confidence": 70, "reason": "", "decisive": False})
    monkeypatch.setattr(engine, "_check_benefic_aspects_to_significators", lambda *a, **k: {"favorable": False})


def test_primary_gate_overrides_denial(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    patch_engine(engine, monkeypatch)
    monkeypatch.setattr(engine, "_primary_perfection_gate", lambda *a, **k: {"passes": True, "reason": "test"})
    monkeypatch.setattr(engine, "_check_enhanced_denial_conditions", lambda *a, **k: {"denied": True, "confidence": 80, "reason": "mock"})

    chart = make_chart()
    result = engine._apply_enhanced_judgment(chart, {})
    assert result["result"] != "NO"


def test_no_gate_allows_denial(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    patch_engine(engine, monkeypatch)
    monkeypatch.setattr(engine, "_primary_perfection_gate", lambda *a, **k: {"passes": False, "reason": "fail"})
    monkeypatch.setattr(engine, "_check_enhanced_denial_conditions", lambda *a, **k: {"denied": True, "confidence": 80, "reason": "mock"})

    chart = make_chart()
    result = engine._apply_enhanced_judgment(chart, {})
    assert result["result"] == "NO"
