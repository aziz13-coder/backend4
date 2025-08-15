import os
import sys

# Ensure modules in parent directory are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import rules
from rule_dump import dump_rules, apply_rule


def test_rules_have_weight_or_fn():
    """Every rule must define a numeric weight or a weight function."""
    for rule in rules.RULES:
        has_numeric = isinstance(rule.get('weight'), (int, float))
        has_fn = isinstance(rule.get('weight_fn'), str)
        assert has_numeric or has_fn, f"Rule {rule.get('id')} missing weight or weight_fn"
        if has_fn:
            assert hasattr(rules, rule['weight_fn']), f"Missing weight function {rule['weight_fn']}"


def test_dump_resolves_weights_and_consumer_works():
    dumped = dump_rules()
    weight_map = {r['id']: r['weight'] for r in dumped}

    # All weights should be numeric after dumping
    for w in weight_map.values():
        assert isinstance(w, (int, float))

    # Consumer should apply weights correctly
    assert apply_rule('static', 10) == 10 * weight_map['static']
    assert apply_rule('dynamic', 10) == 10 * weight_map['dynamic']


def test_extreme_combustion_rule_gating_default_false():
    rule = next(r for r in rules.RULES if r['id'] == 'solar_extreme_combustion_denial')
    assert rule.get('gating') is False
