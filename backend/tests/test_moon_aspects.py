import pytest
from models import Planet, PlanetPosition, Sign, Aspect
from horary_engine.aspects import (
    calculate_moon_next_aspect,
    is_moon_applying_to_aspect,
    is_moon_separating_from_aspect,
)


def make_planet_position(planet, lon, speed, retrograde=False):
    return PlanetPosition(
        planet=planet,
        longitude=lon,
        latitude=0.0,
        house=1,
        sign=Sign.ARIES,
        dignity_score=0,
        retrograde=retrograde,
        speed=speed,
    )


def test_calculate_moon_next_aspect_timing_direct_and_retrograde():
    moon = make_planet_position(Planet.MOON, 10.0, 12.0)
    get_speed = lambda jd: moon.speed

    direct_planet = make_planet_position(Planet.MERCURY, 15.0, 1.0)
    planets = {Planet.MOON: moon, Planet.MERCURY: direct_planet}
    aspect = calculate_moon_next_aspect(planets, 0.0, get_speed)
    assert aspect is not None
    assert aspect.aspect == Aspect.CONJUNCTION
    assert aspect.applying
    assert aspect.perfection_eta_days == pytest.approx(5.0 / 11.0, rel=1e-3)

    retro_planet = make_planet_position(Planet.MERCURY, 15.0, -1.0, retrograde=True)
    planets = {Planet.MOON: moon, Planet.MERCURY: retro_planet}
    aspect = calculate_moon_next_aspect(planets, 0.0, get_speed)
    assert aspect is not None
    assert aspect.aspect == Aspect.CONJUNCTION
    assert aspect.applying
    assert aspect.perfection_eta_days == pytest.approx(5.0 / 13.0, rel=1e-3)


def test_application_and_separation_detection():
    moon_speed = 12.0
    moon = make_planet_position(Planet.MOON, 10.0, moon_speed)
    aspect = Aspect.CONJUNCTION

    direct_app = make_planet_position(Planet.MERCURY, 15.0, 1.0)
    assert is_moon_applying_to_aspect(moon, direct_app, aspect, moon_speed)

    direct_sep = make_planet_position(Planet.MERCURY, 5.0, 1.0)
    assert not is_moon_applying_to_aspect(moon, direct_sep, aspect, moon_speed)
    assert is_moon_separating_from_aspect(moon, direct_sep, aspect, moon_speed)

    retro_app = make_planet_position(Planet.MERCURY, 15.0, -1.0, retrograde=True)
    assert is_moon_applying_to_aspect(moon, retro_app, aspect, moon_speed)

    retro_sep = make_planet_position(Planet.MERCURY, 5.0, -1.0, retrograde=True)
    assert not is_moon_applying_to_aspect(moon, retro_sep, aspect, moon_speed)
    assert is_moon_separating_from_aspect(moon, retro_sep, aspect, moon_speed)

