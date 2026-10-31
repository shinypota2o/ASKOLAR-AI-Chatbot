"""Automated tests. Test case IDs (TC-xx) refer to Test Plan v1.0; TC-29 to TC-31 are new in v0.3 (docs notes)."""
import io
import json
import os
import tempfile
import unittest

from PIL import Image

from askolar import create_app
from askolar.services.expert import evaluate, fields_to_ask, fixed_rule_failures
from askolar.services.facts import FactError, normalize_place, parse_fact
from askolar.services.intent import IntentClassifier
from askolar.services.language import LanguageIdentifier, word_list_language
from askolar.services.smalltalk import classify
from askolar.services.ocr import OCRAdapter, parse_fields


class FakeClassifier(IntentClassifier):
    """Deterministic stand-in for the trained model, so tests do not depend on training results."""
    PHRASES = {
        'paano magluto ng adobo?': ('out_of_scope', 0.95),
        'kailan ang deadline?': ('deadline', 0.9),
        'ano ang requirements?': ('requirements', 0.9),
        'requirements please': ('requirements', 0.9),
        'magkano ang tuition fee?': ('out_of_scope', 0.9),
        'maybe deadline?': ('deadline', 0.3),  # low confidence -> clarify
    }

    def __init__(self):
        super().__init__(None)
        self.mode = 'fake_for_tests'

    def predict(self, text):
        command = self._command(text)
        if command:
            return command, 1.0
        label, conf = self.PHRASES.get(text.strip().lower(), (None, 0.0))
        return (label, conf) if conf >= self.threshold else (None, conf)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True, classifier=FakeClassifier())
        self.client = self.app.test_client()
        self.token = self.client.get('/api/session').json['csrf']

    def send(self, text, lang=None):
        body = {'message': text} if lang is None else {'message': text, 'lang': lang}
        return self.client.post('/api/chat', json=body, headers={'X-CSRF-Token': self.token})

    def run_demo(self, year, gwa):
        for x in ['demo', 'eligibility', 'I agree', year, gwa]:
            last = self.send(x).json
        return last

    # ---------- web and security ----------
    def test_page_and_assets(self):
        for url in ['/', '/static/app.js', '/static/style.css']:
            with self.client.get(url) as response:
                self.assertEqual(response.status_code, 200)

    def test_csrf(self):
        self.assertEqual(self.client.post('/api/chat', json={'message': 'hi'}).status_code, 403)

    def test_input(self):
        for value in ['', None, 42, 'x' * 2001]:
            r = self.client.post('/api/chat', json={'message': value}, headers={'X-CSRF-Token': self.token})
            self.assertEqual(r.status_code, 400)

    # ---------- conversation ----------
    def test_tc09_no_applicable_programs(self):
        only_san_juan = {'schema_version': 2, 'programs': [p for p in json.load(open('data/knowledge_base.json', encoding='utf-8'))['programs']
                                                          if p['id'].startswith('sanjuan')]}
        path = os.path.join(tempfile.mkdtemp(), 'kb.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(only_san_juan, f)
        client = create_app(testing=True, classifier=FakeClassifier(), knowledge_path=path).test_client()
        token = client.get('/api/session').json['csrf']
        r = client.post('/api/chat', json={'message': 'availability'}, headers={'X-CSRF-Token': token}).json
        self.assertIn('No verified scholarship programs open to PGPC', r['text'])

    def test_availability_lists_verified_programs_only(self):
        r = self.send('availability').json
        self.assertIn('Office of BM Melvin Vidal', r['text'])
        self.assertIn('Bokal Marcus Mendoza', r['text'])
        self.assertIn('NOT open to PGPC students: San Juan LYDO', r['text'])
        self.assertNotIn('GVSR', r['text'])  # waiting for OSA permission (hidden)

    def test_tc06_unclear_gets_clarification(self):
        r = self.send('asdf qwe zxc').json
        self.assertIn('did not understand', r['text'])
        self.assertIn('availability', r['options'])

    def test_tc06_low_confidence_is_not_guessed(self):
        self.assertIn('did not understand', self.send('maybe deadline?').json['text'])

    def test_tc07_out_of_scope(self):
        self.assertIn('only answer questions about scholarships', self.send('Paano magluto ng adobo?', 'en').json['text'])
        self.assertIn('Scholarships at educational assistance', self.send('Paano magluto ng adobo?').json['text'])

    def test_tc27_lipa_clarification(self):
        self.assertIn('Please clarify', self.send('taga Lipa ako', 'en').json['text'])
        self.assertIn('Pakilinaw', self.send('taga Lipa ako').json['text'])

    # ---------- v0.3: language, small talk, scope ----------
    def test_tc29_reply_follows_student_language(self):
        r = self.send('Ano ang requirements?').json
        self.assertEqual(r['lang'], 'fil')
        self.assertIn('Aling scholarship', r['text'])
        r = self.send('What are the requirements for Mendoza?').json
        self.assertEqual(r['lang'], 'en')
        self.assertIn('Requirements for Bokal Marcus Mendoza', r['text'])

    def test_tc29_short_answers_keep_language(self):
        self.send('Kailan ang deadline?')
        self.assertEqual(self.send('demo').json['lang'], 'fil')

    def test_tc30_toggle_overrides_detection(self):
        self.assertEqual(self.send('What are the requirements?', 'fil').json['lang'], 'fil')
        self.assertEqual(self.send('Ano ang requirements?', 'en').json['lang'], 'en')

    def test_tc31_greetings_with_po_and_question(self):
        self.assertIn('Hello, iskolar', self.send('Hi po!').json['text'])
        self.assertIn('Hello, iskolar', self.send('good morning po').json['text'])
        r = self.send('Hi po, requirements please', 'fil').json
        self.assertNotIn('Hello, iskolar', r['text'])
        self.assertIn('Aling scholarship', r['text'])  # the question was answered
        self.assertIn('Walang anuman', self.send('salamat po').json['text'])

    def test_hindi_is_not_a_greeting(self):
        self.assertEqual(classify('hindi ko alam')[0], None)

    def test_benefit_amounts_are_not_given(self):
        r = self.send('Magkano ang allowance sa Vidal?').json
        self.assertIn('halaga', r['text'])
        self.assertNotIn('₱', r['text'])
        self.assertIn('Scholarships at educational assistance', self.send('Magkano ang tuition fee?').json['text'])  # not a scholarship

    def test_renewal_status_payout_are_referred(self):
        for q in ['May opportunity po ba na ma-renew ang scholarship every school year?',
                  'Paano po malalaman kung officially accepted na ako bilang scholar?',
                  'Kailan ang payout ng Vidal?', 'What are the renewal requirements?']:
            r = self.send(q).json
            self.assertTrue('renewal' in r['text'], q)
        self.assertIn('Batangas Provincial Capitol', self.send('Kailan ang payout ng Vidal?').json['text'])
        self.assertNotIn('renewal', self.send('Ano ang requirements?', 'en').json['text'])

    def test_programs_page_has_no_hidden_programs(self):
        data = self.client.get('/api/programs').json
        names = [p['name'] for p in data['open']]
        self.assertEqual(len(names), 2)
        self.assertEqual(len(data['not_open']), 1)
        self.assertFalse(any('GVSR' in n for n in names))

    def test_vidal_rules_and_notes(self):
        for x in ['Vidal', 'eligibility', 'I agree', '1.55', '23']:
            r = self.send(x, 'en').json
        r = self.send('confirm', 'en').json
        self.assertEqual(r['result']['overall'], 'POTENTIALLY_MEETS_LISTED_CRITERIA')
        self.assertIn('No failing grade', r['text'])
        self.assertIn('Source: ', 'Source: ' + r['source'])

    def test_mendoza_residency_outside_4th_district(self):
        for x in ['Mendoza', 'eligibility', 'I agree', 'Lobo, Batangas', '1.75', '21']:
            self.send(x, 'en')
        r = self.send('confirm', 'en').json
        self.assertEqual(r['result']['overall'], 'LISTED_CRITERIA_NOT_MET')
        self.assertEqual(r['result']['criteria'][0]['status'], 'UNMET')

    def test_filipino_result_and_reasons(self):
        for x in ['Mendoza', 'eligibility', 'oo', 'Rosario, Batangas', '3.25', '21']:
            self.send(x, 'fil')
        r = self.send('confirm', 'fil').json
        self.assertIn('HINDI PASOK', r['text'])
        self.assertIn('hindi hihigit sa 3.0', r['text'])

    def test_tc04_tc08_info_from_knowledge_base_with_source(self):
        first = self.send('San Juan LYDO').json  # naming a program selects it (general info)
        self.assertIn('Cash assistance', first['text'])
        r = self.send('requirements').json  # follow-up keeps the selected program (TC-04)
        self.assertIn('Certificate of Indigency', r['text'])
        self.assertIn('last verified 2024-12-11', r['source'])
        self.assertIn('not eligible', r['text'])  # not-applicable note is always shown

    def test_tc03_consent_before_any_fact(self):
        self.send('demo')
        r = self.send('eligibility').json
        self.assertIn('Privacy notice', r['text'])
        self.assertIn('I agree', r['options'])
        r = self.send('cancel').json
        self.assertIn('cleared', r['text'])

    def test_tc03_declining_consent_collects_nothing(self):
        self.send('demo')
        self.send('eligibility')
        r = self.send('no').json
        self.assertIn('no personal information', r['text'])

    def test_tc10_tc11_demo_pass_after_confirmation(self):
        r = self.run_demo('3', '1.75')
        self.assertNotIn('result', r)
        self.assertIn('review your answers', r['text'])
        r = self.send('confirm').json
        self.assertEqual(r['result']['overall'], 'POTENTIALLY_MEETS_LISTED_CRITERIA')
        self.assertIn('preliminary guidance only', r['text'])

    def test_tc12_unmet_and_unknown(self):
        self.run_demo('1', 'unknown')
        r = self.send('confirm').json['result']
        self.assertEqual(r['overall'], 'LISTED_CRITERIA_NOT_MET')
        self.assertEqual(r['criteria'][1]['status'], 'UNRESOLVED')

    def test_tc14_why_explains(self):
        self.run_demo('3', '2.50')
        self.send('confirm')
        r = self.send('why').json
        self.assertIn('Here is why', r['text'])
        self.assertIn('at most 2.25', r['text'])

    def test_invalid_gwa_is_refused(self):
        self.send('demo')
        self.send('eligibility')
        self.send('I agree')
        self.send('3')
        r = self.send('6.5').json
        self.assertIn('1.00', r['text'])
        self.assertNotIn('result', self.send('confirm').json)

    def test_not_applicable_program_explained_without_personal_facts(self):
        r = self.send('Pwede ba ako sa San Juan LYDO? eligibility').json
        r = self.send('eligibility').json
        self.assertEqual(r['result']['overall'], 'LISTED_CRITERIA_NOT_MET')
        self.assertIn('Padre Garcia', r['text'])
        self.assertNotIn('Privacy notice', r['text'])

    def test_residency_answer_does_not_switch_program(self):
        self.send('demo')
        app_state = list(self.app.extensions['temporary_sessions'].values())[0]['state']
        app_state['pending'] = 'residency'
        app_state['queue'] = ['residency']
        app_state['consent'] = True
        self.send('San Juan, Batangas')
        self.assertEqual(app_state['program_id'], 'demo-a')

    # ---------- sessions and privacy ----------
    def test_tc18_tc22_session_isolation_and_clear(self):
        self.send('demo')
        other = self.app.test_client()
        token = other.get('/api/session').json['csrf']
        r = other.post('/api/chat', json={'message': 'eligibility'}, headers={'X-CSRF-Token': token})
        self.assertNotIn('FICTIONAL', r.json['text'])
        self.client.post('/api/session/end', headers={'X-CSRF-Token': self.token})
        self.assertEqual(len(self.app.extensions['temporary_sessions']), 1)
        self.assertEqual(self.send('hi').status_code, 401)

    def test_tc19_expiry(self):
        for value in self.app.extensions['temporary_sessions'].values():
            value['seen'] -= 1900
        self.assertEqual(self.send('hi').status_code, 401)



class ExpertSystemTests(unittest.TestCase):
    def program(self, *rules):
        return {'rules_complete': True, 'version': 't', 'rules': list(rules)}

    def test_tc21_empty_rules_never_pass(self):
        self.assertEqual(evaluate({'rules': []}, {}, True)['overall'], 'INSUFFICIENT_POLICY')

    def test_tc21_unconfirmed_or_wrong_scale_never_pass(self):
        p = self.program({'field': 'gwa', 'operator': '<=', 'threshold': 2.0, 'scale': 'gwa_1_to_5'})
        self.assertEqual(evaluate(p, {'gwa': {'value': 1.5, 'scale': 'gwa_1_to_5'}}, False)['overall'], 'NEEDS_MORE_INFORMATION')
        self.assertEqual(evaluate(p, {'gwa': {'value': 90, 'scale': 'percentage'}}, True)['overall'], 'NEEDS_MORE_INFORMATION')

    def test_tc13_gwa_lower_is_better(self):
        p = self.program({'field': 'gwa', 'operator': '<=', 'threshold': 2.0, 'scale': 'gwa_1_to_5'})
        self.assertEqual(evaluate(p, {'gwa': {'value': 1.75, 'scale': 'gwa_1_to_5'}}, True)['criteria'][0]['status'], 'MET')
        self.assertEqual(evaluate(p, {'gwa': {'value': 2.25, 'scale': 'gwa_1_to_5'}}, True)['criteria'][0]['status'], 'UNMET')

    def test_income_maximum(self):
        p = self.program({'field': 'family_income', 'operator': '<=', 'threshold': 250000, 'scale': 'php_per_year'})
        self.assertEqual(evaluate(p, {'family_income': {'value': 180000, 'scale': 'php_per_year'}}, True)['overall'], 'POTENTIALLY_MEETS_LISTED_CRITERIA')

    def test_residency_in_list(self):
        p = self.program({'field': 'residency', 'operator': 'in', 'value': ['Padre Garcia, Batangas'], 'scale': 'municipality'})
        self.assertEqual(evaluate(p, {'residency': {'value': 'padre garcia', 'scale': 'municipality'}}, True)['criteria'][0]['status'], 'MET')
        self.assertEqual(evaluate(p, {'residency': {'value': 'Lipa City', 'scale': 'municipality'}}, True)['criteria'][0]['status'], 'UNMET')

    def test_school_location_is_fixed_for_pgpc(self):
        p = self.program({'field': 'school_municipality', 'operator': 'in', 'value': ['San Juan, Batangas'], 'scale': 'municipality'},
                         {'field': 'residency', 'operator': 'in', 'value': ['San Juan, Batangas'], 'scale': 'municipality'})
        self.assertEqual(fields_to_ask(p), ['residency'])  # school location is never asked
        self.assertEqual(len(fixed_rule_failures(p)), 1)

    def test_fact_parsing(self):
        self.assertEqual(parse_fact('family_income', '₱180,000')['value'], 180000)
        self.assertIsNone(parse_fact('gwa', 'unknown')['value'])
        with self.assertRaises(FactError):
            parse_fact('year_level', 'third')
        self.assertEqual(normalize_place('San Juan Batangas'), normalize_place('San Juan, Batangas'))
        self.assertNotEqual(normalize_place('Batangas City'), normalize_place('San Juan'))


class FakeEngine:
    """Stands in for Tesseract so tests do not depend on OCR quality."""
    def __init__(self, text):
        self.text = text

    def image_to_text(self, path):
        assert os.path.exists(path)  # the file exists only while it is being read
        return self.text


def png_bytes():
    buffer = io.BytesIO()
    Image.new('RGB', (40, 20), 'white').save(buffer, format='PNG')
    return buffer.getvalue()


class OCRTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        text = 'PADRE GARCIA POLYTECHNIC COLLEGE\nYear Level: 3\nTotal Units: 21\nGWA: 1.75'
        self.app = create_app(testing=True, classifier=FakeClassifier(), ocr_adapter=OCRAdapter(FakeEngine(text), self.tmp))
        self.client = self.app.test_client()
        self.token = self.client.get('/api/session').json['csrf']

    def send(self, text):
        return self.client.post('/api/chat', json={'message': text}, headers={'X-CSRF-Token': self.token})

    def upload(self, data=None, mimetype='image/png'):
        return self.client.post('/api/ocr/extract', headers={'X-CSRF-Token': self.token},
                                data={'file': (io.BytesIO(data or png_bytes()), 'grades.png', mimetype)},
                                content_type='multipart/form-data')

    def test_upload_refused_before_consent(self):
        self.assertEqual(self.upload().status_code, 409)

    def test_tc15_tc16_tc20_upload_confirm_and_file_deleted(self):
        for x in ['demo', 'eligibility', 'I agree', '3']:
            r = self.send(x).json
        self.assertIn('upload grade report', r['options'])
        r = self.upload().json
        self.assertIn('GWA: 1.75', r['text'])
        self.assertEqual(os.listdir(self.tmp), [])  # TC-20: deleted right after OCR
        r = self.send('use these values').json
        self.assertIn('(from document)', r['text'])  # student reviews before rules run (FR-14)
        r = self.send('confirm').json
        self.assertEqual(r['result']['overall'], 'POTENTIALLY_MEETS_LISTED_CRITERIA')

    def test_tc17_type_manually_instead(self):
        for x in ['demo', 'eligibility', 'I agree', '3']:
            self.send(x)
        self.upload()
        r = self.send('type manually').json
        self.assertIn('GWA', r['text'])

    def test_not_an_image_is_refused(self):
        for x in ['demo', 'eligibility', 'I agree']:
            self.send(x)
        r = self.upload(b'not an image')
        self.assertEqual(r.status_code, 422)
        self.assertIn('No file was kept', r.json['text'])
        self.assertEqual(os.listdir(self.tmp), [])

    def test_wrong_type_is_refused(self):
        for x in ['demo', 'eligibility', 'I agree']:
            self.send(x)
        self.assertEqual(self.upload(mimetype='application/pdf').status_code, 422)

    def test_parse_fields(self):
        self.assertEqual(parse_fields('General Weighted Average : 1.5\n2nd Year\nUnits Enrolled 18'), {'gwa': 1.5, 'units': 18})
        self.assertEqual(parse_fields('THIRD YEAR  GWA 2,25'), {'gwa': 2.25})  # year level is never taken from a document
        self.assertEqual(parse_fields('Total Units | 23 |GWA= 1.55'), {'gwa': 1.55, 'units': 23})  # PGPC class card
        self.assertEqual(parse_fields('no fields here'), {})


class LanguageTests(unittest.TestCase):
    def test_word_list(self):
        self.assertEqual(word_list_language('What documents do I need?'), 'English')
        self.assertEqual(word_list_language('Ano ang mga kailangang ipasa?'), 'Filipino')
        self.assertEqual(word_list_language('Ano yung requirements for this scholarship?'), 'Taglish')

    def test_too_short_to_tell(self):
        self.assertIsNone(LanguageIdentifier().detect('2.0'))
        self.assertIsNone(LanguageIdentifier().detect('confirm'))


if __name__ == '__main__':
    unittest.main()
