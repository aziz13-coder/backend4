import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from horary_engine import engine as engine_module
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from test_consideration_warnings import make_chart, patch_engine_for_tests


def test_direct_perfection_not_overridden_by_unfavorable_moon(monkeypatch):
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    patch_engine_for_tests(engine, monkeypatch)

    chart = make_chart()
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

    def fake_moon_next_aspect(*args, **kwargs):
        return {
            "decisive": True,
            "result": "NO",
            "confidence": 60,
            "reason": "Moon square Mercury",
            "timing": "1 day",
            "reception": "none",
            "void_moon": False,
        }

    monkeypatch.setattr(
        engine, "_check_moon_next_aspect_to_significators", fake_moon_next_aspect
    )

    result = engine._apply_enhanced_judgment(chart, {})

    assert result["result"] == "YES"
