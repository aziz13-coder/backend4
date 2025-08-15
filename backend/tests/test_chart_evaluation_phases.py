import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluate_chart import evaluate_chart


def test_phase_a_sets_normalization():
    chart = {}
    evaluate_chart(chart)
    assert chart.get('normalized') is True


def test_phase_b_primary_success_returns_yes():
    chart = {'paths': ['direct']}
    result = evaluate_chart(chart)
    assert result['verdict'] == 'YES'
    assert 'path:direct' in result['proof']


def test_phase_c_blocker_overrides_success():
    chart = {'paths': ['direct'], 'blockers': ['prohibition']}
    result = evaluate_chart(chart)
    assert result['verdict'] == 'NO'
    assert 'blocker:prohibition' in result['proof']


def test_phase_d_no_path_default_no():
    chart = {}
    result = evaluate_chart(chart)
    assert result['verdict'] == 'NO'
    assert 'no-path' in result['proof']


def test_phase_e_modulators_adjust_confidence():
    chart = {'paths': ['direct'], 'modulators': {'dignities': 0.2, 'benefics': 0.1}}
    result = evaluate_chart(chart)
    assert result['verdict'] == 'YES'
    assert result['confidence'] == 0.8
