import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from horary_config import cfg
from horary_engine import engine as engine_module
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import HoraryChart, Planet, Sign, PlanetPosition


def make_chart(mercury_dignity=0, mercury_house=1, sun_house=4):
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, mercury_house, Sign.ARIES, mercury_dignity),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 0, 0, 7, Sign.LIBRA, 0),
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 3, Sign.GEMINI, 0),
        Planet.SUN: PlanetPosition(Planet.SUN, 0, 0, sun_house, Sign.CANCER, 0),
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


def setup_engine(engine, monkeypatch, solar_factors):
    def fake_identify_significators(chart, qa):
        return {"valid": True, "querent": Planet.MERCURY, "quesited": Planet.JUPITER, "description": "Mercury-Jupiter"}

    monkeypatch.setattr(engine, "_identify_significators", fake_identify_significators)
    monkeypatch.setattr(engine_module, "check_enhanced_radicality", lambda c, ignore=False: {"valid": True, "reason": "radical"})
    monkeypatch.setattr(engine, "_is_moon_void_of_course_enhanced", lambda c: {"void": False, "exception": False, "reason": ""})
    monkeypatch.setattr(engine, "_analyze_enhanced_solar_factors", lambda *a, **k: solar_factors)
    monkeypatch.setattr(
        engine,
        "_check_enhanced_perfection",
        lambda *a, **k: {
            "perfects": True,
            "favorable": True,
            "confidence": cfg().confidence.base_confidence,
            "type": "direct",
            "reason": "test",
        },
    )
    monkeypatch.setattr(engine, "_apply_aspect_direction_adjustment", lambda c, p, r: c)
    monkeypatch.setattr(engine, "_apply_dignity_confidence_adjustment", lambda c, ch, q, qs, r: c)
    monkeypatch.setattr(engine, "_apply_retrograde_quesited_penalty", lambda c, ch, q, r: c)
    monkeypatch.setattr(engine, "_apply_confidence_threshold", lambda res, conf, reasoning: (res, conf))
    monkeypatch.setattr(engine, "_calculate_enhanced_timing", lambda *a, **k: None)
    monkeypatch.setattr(engine, "_check_traditional_prohibition", lambda *a, **k: {"found": False})
    monkeypatch.setattr(engine, "_check_moon_sun_education_perfection", lambda *a, **k: {"perfects": False})
    monkeypatch.setattr(engine, "_detect_reception_between_planets", lambda *a, **k: "none")


def test_under_beams_penalty_applied(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    solar_factors = {
        "significant": True,
        "summary": "Under Beams: Mercury",
        "cazimi_count": 0,
        "combustion_count": 0,
        "under_beams_count": 1,
        "detailed_analyses": {
            "Mercury": {
                "planet": "Mercury",
                "distance_from_sun": 14.0,
                "condition": "Under the Beams",
                "dignity_modifier": 0,
                "description": "",
                "exact_cazimi": False,
                "traditional_exception": False,
                "effect_ignored": False,
                "penalty_code": "SOL_COMBUSTION_MINOR",
            }
        },
        "combustion_ignored": False,
        "penalty_codes": ["SOL_COMBUSTION_MINOR"],
    }
    chart = make_chart()
    setup_engine(engine, monkeypatch, solar_factors)

    result = engine._apply_enhanced_judgment(chart, {})
    assert result["result"] == "YES"
    assert any("under beams" in r.lower() for r in result["reasoning"])
    expected_confidence = cfg().confidence.base_confidence - cfg().confidence.solar.under_beams_penalty
    assert result["confidence"] == expected_confidence


def test_extreme_combustion_denial_toggle(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    solar_factors = {
        "significant": True,
        "summary": "Combusted: Mercury",
        "cazimi_count": 0,
        "combustion_count": 1,
        "under_beams_count": 0,
        "detailed_analyses": {
            "Mercury": {
                "planet": "Mercury",
                "distance_from_sun": 0.5,
                "condition": "Combustion",
                "dignity_modifier": 0,
                "description": "",
                "exact_cazimi": False,
                "traditional_exception": False,
                "effect_ignored": False,
                "penalty_code": "SOL_COMBUSTION_MAJOR",
            }
        },
        "combustion_ignored": False,
        "penalty_codes": ["SOL_COMBUSTION_MAJOR"],
    }
    chart = make_chart(mercury_dignity=-5, mercury_house=3, sun_house=10)
    setup_engine(engine, monkeypatch, solar_factors)

    original_flag = cfg().solar.extreme_combustion_denial_enabled
    try:
        cfg().solar.extreme_combustion_denial_enabled = True
        result = engine._apply_enhanced_judgment(chart, {})
    finally:
        cfg().solar.extreme_combustion_denial_enabled = original_flag

    assert result["result"] == "NO"
    assert any("extreme combustion" in r.lower() for r in result["reasoning"])
    assert result["confidence"] == 90
