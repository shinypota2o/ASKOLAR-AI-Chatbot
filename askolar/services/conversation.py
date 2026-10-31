"""Conversation Manager (Facade): one entry point that routes each message to the
Intent Classifier, Info Retrieval, Expert System or OCR Service (System Design v0.3, Figure 1).

v0.3: replies follow the student's language (English, or Filipino for Filipino/Taglish),
greetings/thanks/goodbyes are handled by rules, and benefit amounts are not given
(out of scope in SRS v1.0).
"""
import re

from . import composer
from .composer import TOPICS, reply
from .expert import evaluate, fields_to_ask, fixed_rule_failures
from .facts import FACTS, FactError, parse_fact
from .language import reply_language
from .messages import t
from .smalltalk import asks_amount, asks_unsupported, classify

INFO_INTENTS = {'requirements', 'deadline', 'application_procedure', 'general_info'}
SWITCH_CONFIDENCE = 0.70  # how sure the model must be to leave a pending question
CONSENT_WORDS = {'i agree', 'agree', 'yes', 'oo', 'opo', 'sige', 'pumapayag ako', 'payag', 'okay', 'ok'}


def fresh_state():
    return {'program_id': None, 'pending': None, 'queue': [], 'facts': {}, 'confirmed': False,
            'consent': False, 'last_result': None, 'awaiting_program_for': None, 'ocr_candidates': None,
            'lang': 'en'}


class ConversationManager:
    def __init__(self, knowledge, classifier, language=None):
        self.kb, self.classifier, self.language = knowledge, classifier, language

    # ---------- helpers ----------
    def _program(self, state):
        return self.kb.get(state['program_id']) if state['program_id'] else None

    def _program_options(self):
        names = [p['name'] for p in self.kb.applicable_programs()]
        return names or ['availability']

    def _reset_check(self, state):
        state.update(pending=None, queue=[], facts={}, confirmed=False, last_result=None)

    def _set_language(self, state, text, preference):
        """'en'/'fil' from the UI toggle wins; 'auto' follows the student's message."""
        if preference in ('en', 'fil'):
            state['lang'] = preference
        elif self.language is not None:
            detected = reply_language(self.language.detect(text))
            if detected:
                state['lang'] = detected

    # ---------- main entry ----------
    def handle(self, state, message, preference='auto'):
        state.setdefault('lang', 'en')
        text = message.strip()
        self._set_language(state, text, preference)
        lang = state['lang']
        t_lower = text.lower()

        if t_lower == 'demo':
            state.update(fresh_state(), program_id=self.kb.demo['id'], lang=lang)
            return reply(t('demo_selected', lang), ['eligibility', 'requirements'])
        if t_lower == 'cancel':
            self._reset_check(state)
            return reply(t('cancelled', lang), TOPICS)
        if t_lower in {'why', 'bakit', 'explain'} and state['last_result']:
            return composer.explanation(state['last_result'], lang)

        # Greetings, thanks and goodbyes (rules, not an intent). Not while an answer is pending.
        if state['pending'] is None:
            kind, rest = classify(text)
            if kind in ('thanks', 'bye'):
                return reply(t(kind, lang), TOPICS)
            if kind == 'greeting':
                if not rest:
                    return reply(t('greeting', lang), TOPICS)
                text, t_lower = rest, rest.lower()  # "Hi po, ano requirements?" -> the question

        # A program named in the message becomes the selected program, except while an answer
        # is pending (e.g., typing "San Juan" as a residency answer must not switch programs).
        named = None if state['pending'] in FACTS else self.kb.find_in_text(text)
        if named:
            state['program_id'] = named['id']

        if state['pending'] == 'consent':
            return self._handle_consent(state, t_lower)
        if state['pending'] == 'ocr_confirm':
            return self._handle_ocr_confirm(state, t_lower)
        if t_lower == 'upload grade report':
            return reply(t('upload_use_button', lang), ['upload grade report', 'unknown', 'cancel'])
        if state['pending'] == 'review':
            if t_lower == 'confirm':
                return self._evaluate(state)
            if t_lower not in {'eligibility'}:
                return reply(t('review_prompt', lang), ['confirm', 'eligibility', 'cancel'])

        intent, confidence = self.classifier.predict(text)

        # Benefit amounts are out of scope (SRS v1.0), so ASKOLAR never states them.
        # "Magkano ang tuition fee?" is not about a scholarship, so it gets the out-of-scope reply.
        if state['pending'] not in FACTS and intent != 'out_of_scope' and asks_amount(text):
            return reply(t('amounts', lang), TOPICS)
        # Renewals, application status and payout schedules are referred to the office (rule, not an intent).
        if state['pending'] not in FACTS and asks_unsupported(text):
            return self._unsupported(state, named)

        # Location is context, not proof that a request is out of scope (System Design v0.3).
        if re.search(r'\blipa\b', t_lower) and not named and intent != 'out_of_scope' and state['pending'] not in FACTS:
            return reply(t('lipa_clarify', lang), ['pgpc residency', 'external scholarship'])
        if t_lower == 'pgpc residency':
            return reply(t('pgpc_residency', lang), TOPICS)
        if t_lower == 'external scholarship':
            return reply(t('external', lang), TOPICS)

        if state['pending'] in FACTS:
            leaving = intent and intent != 'eligibility' and confidence >= SWITCH_CONFIDENCE and not re.search(r'\d', t_lower)
            if not leaving:
                return self._handle_fact(state, text)
            self._reset_check(state)

        if state['awaiting_program_for'] and named:
            intent = state['awaiting_program_for']
            state['awaiting_program_for'] = None

        if intent is None:
            if named:
                intent = 'general_info'
            else:
                return reply(t('not_understood', lang), TOPICS)
        if intent == 'out_of_scope':
            return reply(t('out_of_scope', lang), TOPICS)
        if intent == 'availability':
            return self._availability(lang)
        if intent == 'eligibility':
            return self._start_eligibility(state)
        if intent in INFO_INTENTS:
            return self._info(state, intent)
        return reply(t('not_understood', lang), TOPICS)

    def _unsupported(self, state, named):
        lang = state['lang']
        text = t('unsupported', lang)
        program = named or self._program(state)
        office = (program or {}).get('office') or {}
        details = '; '.join(v for v in [office.get('address'), office.get('hours'), office.get('contact')] if v)
        if program and details and not program.get('fictional'):
            text += '\n' + t('office_line', lang, name=program['name'], office=details)
        return reply(text, TOPICS, source=composer.source_line(program, lang) if program else None)

    # ---------- intents ----------
    def _availability(self, lang):
        open_programs = self.kb.applicable_programs()
        others = [p for p in self.kb.verified_programs() if p not in open_programs]
        return composer.availability(open_programs, others, lang)

    def _need_program(self, state, intent):
        programs = self.kb.applicable_programs()
        if len(programs) == 1:
            state['program_id'] = programs[0]['id']
            return None
        state['awaiting_program_for'] = intent
        if not programs:
            return reply(t('need_program_none', state['lang']), ['availability', 'demo'])
        return reply(t('which_program', state['lang']), self._program_options())

    def _info(self, state, intent):
        program = self._program(state)
        if not program:
            asked = self._need_program(state, intent)
            if asked:
                return asked
            program = self._program(state)
        return composer.info(program, self.kb.retrieve(program, intent), intent, state['lang'])

    def _start_eligibility(self, state):
        lang = state['lang']
        program = self._program(state)
        if not program:
            asked = self._need_program(state, 'eligibility')
            if asked:
                return asked
            program = self._program(state)
        self._reset_check(state)
        # Rules every PGPC student fails are explained right away, without asking personal facts.
        failures = fixed_rule_failures(program)
        if failures:
            result = {'overall': 'LISTED_CRITERIA_NOT_MET', 'criteria': failures, 'rule_version': program.get('version')}
            state['last_result'] = result
            return composer.result(program, result, lang, ['availability'] + TOPICS[1:])
        if not program.get('rules_complete') or not program.get('rules'):
            return composer.insufficient_policy(program, lang)
        state['queue'] = fields_to_ask(program)
        if not state['consent']:
            state['pending'] = 'consent'
            return reply(t('privacy_notice', lang), ['I agree', 'cancel'])
        return self._next_question(state)

    def _handle_consent(self, state, t_lower):
        if t_lower in CONSENT_WORDS:
            state['consent'] = True
            return self._next_question(state)
        self._reset_check(state)
        return reply(t('consent_declined', state['lang']), TOPICS)

    def _next_question(self, state):
        program = self._program(state)
        if state['queue']:
            state['pending'] = state['queue'][0]
            return composer.fact_question_reply(program, state['pending'], state['lang'])
        state['pending'] = 'review'
        return composer.review(program, state['facts'], state['lang'])

    # ---------- OCR (FR-13, FR-14) ----------
    @staticmethod
    def ocr_allowed(state):
        return state['consent'] and state['pending'] in FACTS

    def handle_ocr(self, state, fields):
        needed = {}
        for field, value in fields.items():
            if field in state['queue'] and field in composer.OCR_FIELDS:
                try:  # OCR values must pass the same checks as typed answers
                    needed[field] = parse_fact(field, str(value))['value']
                except FactError:
                    continue
        if not needed:
            return composer.ocr_nothing_found(state['pending'], state['lang'])
        state['ocr_candidates'] = needed
        state['pending'] = 'ocr_confirm'
        return composer.ocr_candidates(needed, state['lang'])

    def ocr_failed(self, state, message):
        return composer.ocr_failed(message, state['pending'], state.get('lang', 'en'))

    def _handle_ocr_confirm(self, state, t_lower):
        candidates = state['ocr_candidates'] or {}
        state['ocr_candidates'] = None
        if t_lower in {'use these values', 'yes', 'confirm', 'oo', 'opo'}:
            for field, value in candidates.items():
                state['facts'][field] = {'value': value, 'scale': FACTS[field]['scale'], 'from_document': True}
                state['queue'].remove(field)
            return self._next_question(state)
        if t_lower == 'cancel':
            self._reset_check(state)
            return reply(t('cancelled', state['lang']), TOPICS)
        return self._next_question(state)  # "type manually": ask the questions as usual

    def _handle_fact(self, state, text):
        field = state['pending']
        try:
            state['facts'][field] = parse_fact(field, text)
        except FactError as error:
            return reply(t(error.key, state['lang']) + t('or_unknown', state['lang']), ['unknown', 'cancel'])
        state['queue'].pop(0)
        return self._next_question(state)

    def _evaluate(self, state):
        program = self._program(state)
        state['confirmed'] = True
        state['pending'] = None
        result = evaluate(program, state['facts'], confirmed=True)
        state['last_result'] = result
        return composer.result(program, result, state['lang'])
