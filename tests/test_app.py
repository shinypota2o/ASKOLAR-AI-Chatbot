import unittest
from askolar import create_app
from askolar.services.expert import evaluate
class AppTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app(testing=True);self.client=self.app.test_client()
        self.token=self.client.get('/api/session').json['csrf']
    def send(self,text):
        return self.client.post('/api/chat',json={'message':text},headers={'X-CSRF-Token':self.token})
    def test_page_and_assets(self):
        for url in ['/','/static/app.js','/static/style.css']:
            with self.client.get(url) as response:
                self.assertEqual(response.status_code,200)
    def test_csrf(self):self.assertEqual(self.client.post('/api/chat',json={'message':'hi'}).status_code,403)
    def test_input(self):
        for value in ['',None,42,'x'*2001]:
            self.assertEqual(self.client.post('/api/chat',json={'message':value},headers={'X-CSRF-Token':self.token}).status_code,400)
    def test_no_real_policies(self):self.assertIn('No verified',self.send('availability').json['text'])
    def test_unknown_is_not_rejected(self):self.assertIn('not automatically',self.send('random unfamiliar wording').json['text'])
    def test_lipa_clarification(self):self.assertIn('Please clarify',self.send('taga Lipa ako').json['text'])
    def test_demo_pass_confirmation(self):
        for x in ['demo','eligibility','3','88']:result=self.send(x).json
        self.assertNotIn('result',result)
        self.assertEqual(self.send('confirm').json['result']['overall'],'POTENTIALLY_MEETS_LISTED_CRITERIA')
    def test_unmet_and_unknown(self):
        for x in ['demo','eligibility','1','unknown']:self.send(x)
        r=self.send('confirm').json['result'];self.assertEqual(r['overall'],'LISTED_CRITERIA_NOT_MET')
        self.assertEqual(r['criteria'][1]['status'],'UNRESOLVED')
    def test_bad_grade(self):
        for x in ['demo','eligibility','2']:self.send(x)
        self.assertIn('0 to 100',self.send('101').json['text'])
        self.assertNotIn('result',self.send('confirm').json)
    def test_session_isolation_and_clear(self):
        self.send('demo');other=self.app.test_client();token=other.get('/api/session').json['csrf']
        r=other.post('/api/chat',json={'message':'eligibility'},headers={'X-CSRF-Token':token})
        self.assertIn('No verified scholarship',r.json['text'])
        self.client.post('/api/session/end',headers={'X-CSRF-Token':self.token})
        self.assertEqual(len(self.app.extensions['temporary_sessions']),1)
        self.assertEqual(self.send('hi').status_code,401)
    def test_expiry(self):
        for value in self.app.extensions['temporary_sessions'].values():value['seen']-=1900
        self.assertEqual(self.send('hi').status_code,401)
    def test_ocr_honest(self):
        self.assertEqual(self.client.post('/api/ocr/extract',headers={'X-CSRF-Token':self.token}).status_code,501)
    def test_no_empty_rules_pass(self):self.assertEqual(evaluate({'rules':[]}, {}, True)['overall'],'INSUFFICIENT_POLICY')
    def test_scale_and_confirmation(self):
        p={'rules_complete':True,'version':'test','rules':[{'field':'grade','operator':'>=','threshold':85,'scale':'percentage'}]}
        for fact,confirmed in [({'value':88,'scale':'percentage'},False),({'value':1.75,'scale':'GWA'},True)]:
            self.assertEqual(evaluate(p,{'grade':fact},confirmed)['overall'],'NEEDS_MORE_INFORMATION')
if __name__=='__main__':unittest.main()
