"""Rule-Based Expert System: evaluates confirmed facts against verified IF-THEN rules.

Each criterion is MET, UNMET or UNRESOLVED. A missing fact, an unconfirmed fact, a
wrong scale or an incomplete rule set can never produce an automatic pass (SRS NFR-11).
"""
import math

from .facts import FACTS, FIXED_FACTS, normalize_place
from .messages import t

SUPPORTED_OPERATORS = {'>=', '<=', 'in', '=='}


def _is_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _label(rule):
    field = rule.get('field', '')
    if field in FACTS:
        return FACTS[field]['label']
    return rule.get('label') or field.replace('_', ' ').capitalize()


def _check(rule, fact):
    """Return (status, reason_key, params) for one rule and one fact."""
    op = rule.get('operator')
    if op not in SUPPORTED_OPERATORS:
        return 'UNRESOLVED', 'reason_policy', {}
    if fact is None or fact.get('value') is None:
        return 'UNRESOLVED', 'reason_not_provided', {}
    if fact.get('scale') != rule.get('scale'):
        return 'UNRESOLVED', 'reason_scale', {}
    value = fact['value']

    if op in ('>=', '<='):
        threshold = rule.get('threshold')
        if not (_is_number(threshold) and _is_number(value)):
            return 'UNRESOLVED', 'reason_numeric', {}
        met = value >= threshold if op == '>=' else value <= threshold
        key = 'reason_at_least' if op == '>=' else 'reason_at_most'
        return ('MET' if met else 'UNMET'), key, {'value': value, 'threshold': threshold}

    allowed = rule.get('value')
    if op == '==':
        allowed = [allowed]
    if not isinstance(allowed, list) or not allowed:
        return 'UNRESOLVED', 'reason_list', {}
    if rule.get('scale') == 'municipality':
        ok = normalize_place(str(value)) in {normalize_place(str(a)) for a in allowed}
    else:
        ok = value in allowed
    return ('MET' if ok else 'UNMET'), 'reason_accepted', {'value': value, 'allowed': ', '.join(map(str, allowed))}


def _criterion(rule, status, key, params):
    """One criterion of a result; 'reason' is English, 'reason_key' lets the composer translate it."""
    return {'field': rule.get('field'), 'label': _label(rule), 'status': status,
            'reason': t(key, 'en', **params), 'reason_key': key, 'params': params}


def fields_to_ask(program):
    """Facts the student must provide for this program (never the fixed ones)."""
    seen = []
    for rule in program.get('rules', []):
        field = rule.get('field')
        if field in FACTS and field not in seen:
            seen.append(field)
    return seen


def fixed_rule_failures(program):
    """Rules every PGPC student fails, e.g., the school must be in another town."""
    failures = []
    for rule in program.get('rules', []):
        field = rule.get('field')
        if field in FIXED_FACTS:
            status, _key, _params = _check(rule, FIXED_FACTS[field])
            if status == 'UNMET':
                allowed = rule.get('value') if isinstance(rule.get('value'), list) else [rule.get('value')]
                params = {'allowed': ' or '.join(map(str, allowed)), 'pgpc': FIXED_FACTS[field]['value']}
                failures.append(_criterion(rule, status, 'reason_school', params))
    return failures


def evaluate(program, facts, confirmed=False):
    rules = program.get('rules', [])
    if not program.get('rules_complete') or not rules:
        return {'overall': 'INSUFFICIENT_POLICY', 'criteria': [], 'rule_version': program.get('version')}
    criteria = []
    for rule in rules:
        field = rule.get('field')
        if field in FIXED_FACTS:
            fact = FIXED_FACTS[field]
        else:
            fact = facts.get(field) if confirmed else None
        status, key, params = _check(rule, fact)
        if not confirmed and field not in FIXED_FACTS:
            key, params = 'reason_confirm', {}
        criteria.append(_criterion(rule, status, key, params))
    statuses = {c['status'] for c in criteria}
    if 'UNMET' in statuses:
        overall = 'LISTED_CRITERIA_NOT_MET'
    elif 'UNRESOLVED' in statuses:
        overall = 'NEEDS_MORE_INFORMATION'
    else:
        overall = 'POTENTIALLY_MEETS_LISTED_CRITERIA'
    return {'overall': overall, 'criteria': criteria, 'rule_version': program.get('version')}
