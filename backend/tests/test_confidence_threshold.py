import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine


def test_yes_confidence_below_30_is_inconclusive():
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    reasoning = []
    result, conf = engine._apply_confidence_threshold("YES", 25, reasoning)
    assert result == "INCONCLUSIVE"
    assert conf == 25
    assert any("Very low confidence" in r for r in reasoning)


def test_yes_confidence_between_30_and_50_remains_yes_with_warning():
    engine = EnhancedTraditionalHoraryJudgmentEngine()
    reasoning = []
    result, conf = engine._apply_confidence_threshold("YES", 40, reasoning)
    assert result == "YES"
    assert conf == 40
    assert any("Low confidence" in r for r in reasoning)
