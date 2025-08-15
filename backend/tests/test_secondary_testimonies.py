import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_engine import engine as engine_module
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import (
    HoraryChart,
    Planet,
    Sign,
    PlanetPosition,
    Aspect,
    AspectInfo,
    LunarAspect,
)


def _base_chart():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 1, Sign.ARIES, 0),
        Planet.SATURN: PlanetPosition(Planet.SATURN, 180, 0, 7, Sign.LIBRA, 0),
        Planet.MOON: PlanetPosition(Planet.MOON, 10, 0, 3, Sign.GEMINI, 0),
        Planet.VENUS: PlanetPosition(Planet.VENUS, 40, 0, 2, Sign.TAURUS, 0),
        Planet.JUPITER: PlanetPosition(Planet.JUPITER, 220, 0, 9, Sign.SAGITTARIUS, 0),
        Planet.SUN: PlanetPosition(Planet.SUN, 300, 0, 4, Sign.CAPRICORN, 0),
    }
    houses = [i * 30 for i in range(12)]
    house_rulers = {1: Planet.MERCURY, 7: Planet.SATURN}
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


def _setup_engine(engine, monkeypatch):
    def fake_identify_significators(chart, qa):
        return {
            "valid": True,
            "querent": Planet.MERCURY,
            "quesited": Planet.SATURN,
            "description": "Mercury-Saturn",
        }

    monkeypatch.setattr(engine, "_identify_significators", fake_identify_significators)
    monkeypatch.setattr(
        engine_module,
        "check_enhanced_radicality",
        lambda c, ignore=False: {"valid": True, "reason": "radical"},
    )
    monkeypatch.setattr(
        engine, "_is_moon_void_of_course_enhanced", lambda c: {"void": False, "exception": False, "reason": ""}
    )
    monkeypatch.setattr(engine, "_analyze_enhanced_solar_factors", lambda *a, **k: {"significant": False})
    monkeypatch.setattr(engine, "_check_enhanced_perfection", lambda *a, **k: {"perfects": False})
    monkeypatch.setattr(engine, "_apply_aspect_direction_adjustment", lambda c, p, r: c)
    monkeypatch.setattr(engine, "_apply_dignity_confidence_adjustment", lambda c, ch, q, qs, r: c)
    monkeypatch.setattr(engine, "_apply_retrograde_quesited_penalty", lambda c, ch, q, r: c)
    monkeypatch.setattr(engine, "_apply_confidence_threshold", lambda res, conf, reasoning: (res, conf))
    monkeypatch.setattr(engine, "_calculate_enhanced_timing", lambda *a, **k: None)
    monkeypatch.setattr(engine, "_check_enhanced_moon_testimony", lambda *a, **k: {})
    monkeypatch.setattr(engine, "_check_enhanced_denial_conditions", lambda *a, **k: {"denied": False})


def test_moon_next_aspect_only_yields_no(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    _setup_engine(engine, monkeypatch)

    chart = _base_chart()
    chart.moon_next_aspect = LunarAspect(
        planet=Planet.MERCURY,
        aspect=Aspect.TRINE,
        orb=1.0,
        degrees_difference=1.0,
        perfection_eta_days=1.0,
        perfection_eta_description="1 day",
    )

    monkeypatch.setattr(engine, "_check_benefic_aspects_to_significators", lambda *a, **k: {"favorable": False})

    result = engine._apply_enhanced_judgment(chart, {})

    assert result["result"] == "NO"
    assert result["confidence"] == 60


def test_benefic_support_only_yields_no(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    _setup_engine(engine, monkeypatch)

    chart = _base_chart()
    chart.aspects = [
        AspectInfo(
            planet1=Planet.VENUS,
            planet2=Planet.MERCURY,
            aspect=Aspect.SEXTILE,
            orb=1.0,
            applying=True,
            degrees_to_exact=1.0,
        )
    ]

    monkeypatch.setattr(
        engine, "_check_moon_next_aspect_to_significators", lambda *a, **k: {"decisive": False}
    )

    result = engine._apply_enhanced_judgment(chart, {})

    assert result["result"] == "NO"
    assert result["confidence"] == 60

