import datetime
import importlib.util
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from models import Planet, Sign, PlanetPosition, HoraryChart

# Load reception module directly to avoid heavy package imports
spec = importlib.util.spec_from_file_location(
    "reception", Path(__file__).resolve().parent.parent / "horary_engine" / "reception.py"
)
reception = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reception)
TraditionalReceptionCalculator = reception.TraditionalReceptionCalculator


def make_chart(positions):
    houses = [i * 30 for i in range(12)]
    planets = {}
    for planet, (sign, degree) in positions.items():
        longitude = sign.start_degree + degree
        planets[planet] = PlanetPosition(
            planet=planet,
            longitude=longitude,
            latitude=0.0,
            house=1,
            sign=sign,
            dignity_score=0,
        )
    now = datetime.datetime.utcnow()
    return HoraryChart(
        date_time=now,
        date_time_utc=now,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=houses,
        house_rulers={i + 1: Planet.SUN for i in range(12)},
        ascendant=0.0,
        midheaven=0.0,
    )


def test_unilateral_term_reception():
    chart = make_chart({
        Planet.MERCURY: (Sign.LEO, 15),
        Planet.VENUS: (Sign.ARIES, 15),
        Planet.SUN: (Sign.ARIES, 0),
    })
    calc = TraditionalReceptionCalculator()
    res = calc.calculate_comprehensive_reception(chart, Planet.MERCURY, Planet.VENUS)
    assert res["type"] == "unilateral"
    assert res["details"]["receiving_planet"] == Planet.MERCURY
    assert "term" in res["details"]["dignities"]
    assert "term" in res["planet1_receives_planet2"]
    assert not res["planet2_receives_planet1"]


def test_mutual_face_reception():
    chart = make_chart({
        Planet.SUN: (Sign.LIBRA, 0),
        Planet.MOON: (Sign.GEMINI, 20),
    })
    calc = TraditionalReceptionCalculator()
    res = calc.calculate_comprehensive_reception(chart, Planet.SUN, Planet.MOON)
    assert res["type"] == "mutual_face"
    assert "face" in res["planet1_receives_planet2"]
    assert "face" in res["planet2_receives_planet1"]
