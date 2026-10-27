"""Minimal numeric >= rule evaluator. No missing fact can automatically pass."""
import math
def evaluate(program, facts, confirmed=False):
    rules = program.get('rules', [])
    if not program.get('rules_complete') or not rules:
        return {'overall':'INSUFFICIENT_POLICY', 'criteria':[]}
    criteria=[]
    for rule in rules:
        fact=facts.get(rule.get('field'))
        status='UNRESOLVED'
        reason='A confirmed value with the correct scale is required.'
        threshold=rule.get('threshold')
        supported=(rule.get('operator') == '>=' and type(threshold) in (float,int)
                   and math.isfinite(threshold))
        if not supported:
            reason='This rule requires a supported evaluator or policy clarification.'
        elif confirmed and fact and fact.get('scale') == rule.get('scale'):
            value=fact.get('value')
            if type(value) in (int,float) and math.isfinite(value):
                status='MET' if value >= threshold else 'UNMET'
                reason=f'{value} compared with minimum {threshold} ({rule["scale"]}).'
        criteria.append({'field':rule.get('field'), 'status':status, 'reason':reason})
    statuses={c['status'] for c in criteria}
    overall=('LISTED_CRITERIA_NOT_MET' if 'UNMET' in statuses else
             'NEEDS_MORE_INFORMATION' if 'UNRESOLVED' in statuses else
             'POTENTIALLY_MEETS_LISTED_CRITERIA')
    return {'overall':overall, 'criteria':criteria, 'rule_version':program['version']}
