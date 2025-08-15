import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_config import cfg
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import HoraryChart, Planet, Sign, PlanetPosition


def make_chart():
    now = datetime.datetime.utcnow()
    planets = {
        Planet.MARS: PlanetPosition(Planet.MARS, 0, 0, 1, Sign.ARIES, 0, 0),
        Planet.MERCURY: PlanetPosition(Planet.MERCURY, 0, 0, 7, Sign.GEMINI, 12, 12, True),
    }
    houses = [i * 30 for i in range(12)]
    house_rulers = {1: Planet.MARS, 7: Planet.MERCURY}
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


def test_retrograde_penalty_configurable_and_offset_by_dignity():
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    chart = make_chart()
    reasoning = []
    base_confidence = 80

    original_penalty = cfg().retrograde.quesited_penalty
    try:
        cfg().retrograde.quesited_penalty = 12
        confidence = engine._apply_retrograde_quesited_penalty(base_confidence, chart, Planet.MERCURY, reasoning)
        assert confidence == base_confidence - 12

        confidence = engine._apply_dignity_confidence_adjustment(confidence, chart, Planet.MARS, Planet.MERCURY, reasoning)
        assert confidence == base_confidence - 12 + 15
    finally:
        cfg().retrograde.quesited_penalty = original_penalty
