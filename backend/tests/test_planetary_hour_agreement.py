import os
import sys
import datetime

# Allow importing modules from the backend package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from horary_config import cfg
from horary_engine.radicality import (
    check_enhanced_radicality,
    PLANET_SEQUENCE,
    PLANETARY_DAY_RULERS,
)
from models import HoraryChart, Planet, Sign, PlanetPosition
import swisseph as swe


def compute_hour_ruler(dt: datetime.datetime, lat: float, lon: float) -> Planet:
    """Utility function to compute planetary hour ruler for tests."""
    jd = swe.julday(
        dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 + dt.second / 3600
    )
    jd0 = swe.julday(dt.year, dt.month, dt.day, 0.0)

    sunrise_today = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE, (lon, lat, 0))[1][0]
    sunset_today = swe.rise_trans(jd0, swe.SUN, swe.CALC_SET, (lon, lat, 0))[1][0]

    if jd >= sunrise_today:
        sunrise_prev = sunrise_today
        sunset_prev = sunset_today
        sunrise_next = swe.rise_trans(jd0 + 1, swe.SUN, swe.CALC_RISE, (lon, lat, 0))[1][0]
    else:
        sunrise_prev = swe.rise_trans(jd0 - 1, swe.SUN, swe.CALC_RISE, (lon, lat, 0))[1][0]
        sunset_prev = swe.rise_trans(jd0 - 1, swe.SUN, swe.CALC_SET, (lon, lat, 0))[1][0]
        sunrise_next = sunrise_today

    y, m, d, h = swe.revjul(sunrise_today, swe.GREG_CAL)
    sunrise_today_dt = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        hours=h
    )
    weekday = dt.weekday()
    if dt < sunrise_today_dt:
        weekday = (weekday - 1) % 7
    day_ruler = PLANETARY_DAY_RULERS[weekday]

    if sunrise_prev <= jd < sunset_prev:
        hour_len = (sunset_prev - sunrise_prev) / 12
        hour_index = int((jd - sunrise_prev) / hour_len)
    else:
        hour_len = (sunrise_next - sunset_prev) / 12
        hour_index = 12 + int((jd - sunset_prev) / hour_len)

    start_idx = PLANET_SEQUENCE.index(day_ruler)
    return PLANET_SEQUENCE[(start_idx + hour_index) % 7]


@pytest.mark.parametrize(
    "enabled, matches, expected",
    [
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, True),
    ],
)
def test_planetary_hour_agreement(monkeypatch, enabled, matches, expected):
    config = cfg()
    monkeypatch.setattr(config.radicality, "hour_agreement_enabled", enabled)
    monkeypatch.setattr(config.radicality, "hour_agreement_mode", "ruler")

    base_dt = datetime.datetime(2024, 9, 2, 12, 0, tzinfo=datetime.timezone.utc)
    hour_ruler = compute_hour_ruler(base_dt, 0.0, 0.0)

    matching_sign = next(s for s in Sign if s.ruler == hour_ruler)
    non_matching_sign = next(s for s in Sign if s.ruler != hour_ruler)

    dt = base_dt
    asc_sign = matching_sign if matches else non_matching_sign

    asc_degree = asc_sign.value[0] + 10  # 10 degrees into the sign

    planets = {
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 1, Sign.ARIES, 0),
        Planet.SATURN: PlanetPosition(Planet.SATURN, 0, 0, 1, Sign.ARIES, 0),
    }

    chart = HoraryChart(
        date_time=dt,
        date_time_utc=dt,
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={i: Planet.MARS for i in range(1, 13)},
        ascendant=asc_degree,
        midheaven=0.0,
    )

    result = check_enhanced_radicality(chart)
    assert result["valid"] is expected


@pytest.mark.parametrize(
    "base_date, offset_type",
    [
        (datetime.date(2024, 6, 24), "midday"),  # Long summer day
        (datetime.date(2024, 12, 21), "midday"),  # Short winter day
        (datetime.date(2024, 6, 24), "before_sunrise"),
        (datetime.date(2024, 6, 24), "after_sunset"),
    ],
)
def test_planetary_hour_varied_day_lengths_and_twilight(monkeypatch, base_date, offset_type):
    config = cfg()
    monkeypatch.setattr(config.radicality, "hour_agreement_enabled", True)
    monkeypatch.setattr(config.radicality, "hour_agreement_mode", "ruler")

    lat, lon = 51.5, 0.0
    jd0 = swe.julday(base_date.year, base_date.month, base_date.day, 0.0)
    sunrise = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE, (lon, lat, 0))[1][0]
    sunset = swe.rise_trans(jd0, swe.SUN, swe.CALC_SET, (lon, lat, 0))[1][0]

    if offset_type == "midday":
        target_jd = sunrise + (sunset - sunrise) / 2
    elif offset_type == "before_sunrise":
        target_jd = sunrise - 5 / (24 * 60)
    else:  # after_sunset
        target_jd = sunset + 5 / (24 * 60)

    y, m, d, h = swe.revjul(target_jd, swe.GREG_CAL)
    dt = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc) + datetime.timedelta(hours=h)

    hour_ruler = compute_hour_ruler(dt, lat, lon)
    match_sign = next(s for s in Sign if s.ruler == hour_ruler)
    mismatch_sign = next(s for s in Sign if s.ruler != hour_ruler)

    asc_degree_match = match_sign.value[0] + 10
    asc_degree_mismatch = mismatch_sign.value[0] + 10

    planets = {
        Planet.MOON: PlanetPosition(Planet.MOON, 0, 0, 1, Sign.ARIES, 0),
        Planet.SATURN: PlanetPosition(Planet.SATURN, 0, 0, 1, Sign.ARIES, 0),
    }

    chart_match = HoraryChart(
        date_time=dt,
        date_time_utc=dt,
        timezone_info="UTC",
        location=(lat, lon),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={i: Planet.MARS for i in range(1, 13)},
        ascendant=asc_degree_match,
        midheaven=0.0,
    )

    chart_mismatch = HoraryChart(
        date_time=dt,
        date_time_utc=dt,
        timezone_info="UTC",
        location=(lat, lon),
        location_name="Test",
        planets=planets,
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={i: Planet.MARS for i in range(1, 13)},
        ascendant=asc_degree_mismatch,
        midheaven=0.0,
    )

    assert check_enhanced_radicality(chart_match)["valid"] is True
    assert check_enhanced_radicality(chart_mismatch)["valid"] is False
