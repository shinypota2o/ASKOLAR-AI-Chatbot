"""Response Composer: turns service results into a clear reply with source, explanation
and next-step options (System Design v0.3, Figure 1, steps 5-6).

Every reply is written in English ('en') or Filipino ('fil'); see services/messages.py.
Option values stay as commands (e.g., 'requirements'); the Web Chat UI shows a
friendly English or Filipino label for each one.
"""
from .messages import fact_label, fact_question, t, topic_name

TOPICS = ['availability', 'requirements', 'eligibility', 'deadline', 'application procedure', 'general info']
OCR_FIELDS = {'gwa', 'units'}  # printed or written on a class card / grade report


def reply(text, options=None, **extra):
    """Common reply format sent to the Web Chat UI."""
    extra = {k: v for k, v in extra.items() if v is not None}
    return dict(text=text, options=options or [], **extra)


def _demo_prefix(program, lang):
    return t('fictional', lang) if program and program.get('fictional') else ''


def _notes(program, lang):
    notes = program.get('notes') or []
    return ('\n\n' + t('notes_head', lang) + '\n' + '\n'.join(f'• {n}' for n in notes)) if notes else ''


def source_line(program, lang='en'):
    if not program or not program.get('source'):
        return None
    verified = program.get('last_verified')
    return program['source'] + (f' ({t("last_verified", lang, date=verified)})' if verified else '')


def info(program, retrieved, intent, lang='en'):
    """Info Retrieval result -> reply. Missing information is never invented (FR-09)."""
    if not retrieved:
        return reply(t('info_missing', lang, topic=topic_name(intent, lang), name=program['name']), TOPICS,
                     source=source_line(program, lang))
    text = retrieved['answer']
    if intent == 'requirements':
        text = t('requirements_head', lang, name=program['name']) + '\n' + text
    if intent == 'general_info':
        text += _notes(program, lang)
    if program.get('applicable_to_pgpc') is False:
        text += f'\n\n{t("note", lang)}: ' + program['not_applicable_reason']
    return reply(text, TOPICS, source=source_line(program, lang), version=retrieved['version'])


def availability(open_programs, other_programs, lang='en'):
    note = ''
    if other_programs:
        note = '\n\n' + t('avail_others', lang, names=', '.join(p['name'] for p in other_programs))
    if not open_programs:
        return reply(t('avail_none', lang) + note, ['demo'] + [p['name'] for p in other_programs])
    lines = [f'{i}. {p["name"]}' for i, p in enumerate(open_programs, 1)]
    return reply(t('avail_head', lang) + '\n' + '\n'.join(lines) + '\n' + t('avail_choose', lang) + note,
                 [p['name'] for p in open_programs])


def fact_question_reply(program, field, lang='en'):
    options = (['upload grade report'] if field in OCR_FIELDS else []) + ['unknown', 'cancel']
    hint = t('upload_hint', lang) if field in OCR_FIELDS else ''
    return reply(_demo_prefix(program, lang) + fact_question(field, lang) + t('unknown_hint', lang) + hint, options)


def ocr_candidates(fields, lang='en'):
    lines = [f'{fact_label(k, lang)}: {v}' for k, v in fields.items()]
    return reply(t('ocr_head', lang) + '\n' + '\n'.join(lines) + '\n' + t('ocr_tail', lang),
                 ['use these values', 'type manually', 'cancel'])


def ocr_nothing_found(field, lang='en'):
    return reply(t('ocr_nothing', lang) + '\n' + fact_question(field, lang), ['unknown', 'cancel'])


def ocr_failed(message, field, lang='en'):
    text = message + t('ocr_no_file_kept', lang)
    if field and field in OCR_FIELDS | {'year_level', 'family_income', 'residency'}:
        text += '\n' + fact_question(field, lang)
    return reply(text, ['unknown', 'cancel'])


def review(program, facts, lang='en'):
    lines = [f'{fact_label(k, lang)}: {v["value"] if v["value"] is not None else t("not_provided", lang)}'
             + (t('from_document', lang) if v.get('from_document') else '') for k, v in facts.items()]
    return reply(_demo_prefix(program, lang) + t('review_head', lang) + '\n' + '\n'.join(lines) + '\n'
                 + t('review_tail', lang), ['confirm', 'eligibility', 'cancel'])


def _criterion_text(c, lang, sep):
    label = fact_label(c['field'], lang) if c.get('field') in {'year_level', 'gwa', 'family_income', 'residency', 'units'} \
        else c['label']
    reason = t(c['reason_key'], lang, **c.get('params', {})) if c.get('reason_key') else c['reason']
    return f'{label}: {t("status_" + c["status"], lang)}{sep}{reason}'


def result(program, outcome, lang='en', options=None):
    """Expert System result -> reply with every criterion, its reason and the disclaimer (FR-12)."""
    lines = [f'{_demo_prefix(program, lang)}{program["name"]}: {t("overall_" + outcome["overall"], lang)}']
    lines += [_criterion_text(c, lang, '. ') for c in outcome['criteria']]
    text = '\n'.join(lines) + _notes(program, lang) + '\n\n' + t('disclaimer', lang)
    return reply(text, options or ['why', 'requirements', 'availability'], result=outcome,
                 source=source_line(program, lang))


def explanation(outcome, lang='en'):
    lines = [_criterion_text(c, lang, ' — ') for c in outcome['criteria']]
    return reply(t('why_head', lang) + '\n' + '\n'.join(lines) + '\n' + t('only_listed', lang) + ' '
                 + t('disclaimer', lang), TOPICS)


def insufficient_policy(program, lang='en'):
    return reply(t('overall_INSUFFICIENT_POLICY', lang) + t('ask_office', lang) + _notes(program, lang), TOPICS,
                 source=source_line(program, lang))
