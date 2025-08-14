"""Radicality checks for horary charts."""

from typing import Any, Dict

from horary_config import cfg
from models import HoraryChart, Planet, Sign


PLANET_SEQUENCE = [
    Planet.SATURN,
    Planet.JUPITER,
    Planet.MARS,
    Planet.SUN,
    Planet.VENUS,
    Planet.MERCURY,
    Planet.MOON,
]

PLANETARY_DAY_RULERS = {
    0: Planet.MOON,  # Monday
    1: Planet.MARS,  # Tuesday
    2: Planet.MERCURY,  # Wednesday
    3: Planet.JUPITER,  # Thursday
    4: Planet.VENUS,  # Friday
    5: Planet.SATURN,  # Saturday
    6: Planet.SUN,  # Sunday
}


def _sign_triplicity(sign: Sign) -> str:
    """Return the elemental triplicity for a sign."""
    if sign in {Sign.ARIES, Sign.LEO, Sign.SAGITTARIUS}:
        return "fire"
    if sign in {Sign.TAURUS, Sign.VIRGO, Sign.CAPRICORN}:
        return "earth"
    if sign in {Sign.GEMINI, Sign.LIBRA, Sign.AQUARIUS}:
        return "air"
    return "water"


def check_planetary_hour_agreement(chart: HoraryChart, config) -> Dict[str, Any]:
    """Check if planetary hour ruler agrees with Ascendant ruler."""

    dt = chart.date_time
    weekday = dt.weekday()
    day_ruler = PLANETARY_DAY_RULERS.get(weekday, Planet.SUN)
    hour_index = dt.hour
    start_idx = PLANET_SEQUENCE.index(day_ruler)
    hour_ruler = PLANET_SEQUENCE[(start_idx + hour_index) % 7]

    asc_sign = list(Sign)[int((chart.ascendant % 360) // 30)]
    asc_ruler = asc_sign.ruler

    mode = getattr(config.radicality, "hour_agreement_mode", "ruler")

    if mode == "ruler":
        if hour_ruler == asc_ruler:
            return {
                "valid": True,
                "reason": f"Planetary hour ruler {hour_ruler.value} matches Ascendant ruler",
            }
        return {
            "valid": False,
            "reason": (
                f"Planetary hour ruler {hour_ruler.value} does not match Ascendant ruler {asc_ruler.value}"
            ),
        }

    if mode == "sign":
        hour_pos = chart.planets.get(hour_ruler)
        if hour_pos and hour_pos.sign == asc_sign:
            return {
                "valid": True,
                "reason": (
                    f"Planetary hour ruler {hour_ruler.value} in Ascendant sign {asc_sign.sign_name}"
                ),
            }
        return {
            "valid": False,
            "reason": (
                f"Planetary hour ruler {hour_ruler.value} not in Ascendant sign {asc_sign.sign_name}"
            ),
        }

    if mode == "triplicity":
        hour_pos = chart.planets.get(hour_ruler)
        if hour_pos and _sign_triplicity(hour_pos.sign) == _sign_triplicity(asc_sign):
            return {
                "valid": True,
                "reason": (
                    "Planetary hour ruler shares triplicity with Ascendant"
                ),
            }
        return {
            "valid": False,
            "reason": (
                "Planetary hour ruler does not share triplicity with Ascendant"
            ),
        }

    # Unsupported mode - default to valid
    return {"valid": True, "reason": "Unsupported hour agreement mode"}


def check_enhanced_radicality(chart: HoraryChart, ignore_saturn_7th: bool = False) -> Dict[str, Any]:
    """Enhanced radicality checks with configuration"""

    config = cfg()
    asc_degree = chart.ascendant % 30

    # Too early
    if asc_degree < config.radicality.asc_too_early:
        return {
            "valid": False,
            "reason": f"Ascendant too early at {asc_degree:.1f}° - question premature or not mature",
        }

    # Too late
    if asc_degree > config.radicality.asc_too_late:
        return {
            "valid": False,
            "reason": f"Ascendant too late at {asc_degree:.1f}° - question too late or already decided",
        }

    # Saturn in 7th house (configurable)
    if config.radicality.saturn_7th_enabled and not ignore_saturn_7th:
        saturn_pos = chart.planets[Planet.SATURN]
        if saturn_pos.house == 7:
            return {
                "valid": False,
                "reason": "Saturn in 7th house - astrologer may err in judgment (Bonatti)",
            }

    # Via Combusta (configurable)
    if config.radicality.via_combusta_enabled:
        moon_pos = chart.planets[Planet.MOON]
        moon_degree_in_sign = moon_pos.longitude % 30

        via_combusta = config.radicality.via_combusta

        if (
            (moon_pos.sign == Sign.LIBRA and moon_degree_in_sign > via_combusta.libra_start)
            or (
                moon_pos.sign == Sign.SCORPIO
                and moon_degree_in_sign <= via_combusta.scorpio_end
            )
        ):
            return {
                "valid": False,
                "reason": (
                    f"Moon in Via Combusta ({moon_pos.sign.sign_name} {moon_degree_in_sign:.1f}°) - "
                    "volatile or corrupted matter"
                ),
            }

    # Planetary hour agreement (configurable)
    if getattr(config.radicality, "hour_agreement_enabled", False):
        hour_check = check_planetary_hour_agreement(chart, config)
        if not hour_check["valid"]:
            return hour_check

    return {
        "valid": True,
        "reason": f"Chart is radical - Ascendant at {asc_degree:.1f}°",
    }
