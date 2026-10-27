import re
from .composer import reply
from .expert import evaluate
TOPICS=['availability','requirements','eligibility','deadline','application procedure','general info']
def fresh_state():
    return {'program_id':None,'pending':None,'facts':{},'confirmed':False,'last_result':None}
class ConversationManager:
    def __init__(self, knowledge, classifier, demo):
        self.kb, self.classifier, self.demo = knowledge, classifier, demo
    def handle(self, state, message):
        t=message.strip().lower()
        if t=='demo':
            state.update(fresh_state());state['program_id']='demo-a'
            return reply('FICTIONAL DEMO selected. These are not PGPC policies. Try eligibility or view the sample information.', TOPICS)
        if t=='cancel':
            state['pending']=None;state['facts']={};state['confirmed']=False;state['last_result']=None
            return reply('Check cancelled. Temporary answers cleared.', TOPICS)
        if t=='confirm' and state['pending']=='review':
            state['confirmed']=True;state['pending']=None
            result=evaluate(self.demo,state['facts'],confirmed=True);state['last_result']=result
            lines=['FICTIONAL DEMO — preliminary result: '+result['overall']]
            lines += [f'{c["field"]}: {c["status"]}. {c["reason"]}' for c in result['criteria']]
            lines.append('This is not scholarship approval. Final decisions belong to the scholarship office.')
            return reply('\n'.join(lines), ['eligibility','requirements'], result=result, source=self.demo['source'])
        if t in {'why','bakit','explain'} and state['last_result']:
            r=state['last_result']
            return reply('FICTIONAL DEMO: '+ '\n'.join(c['field']+': '+c['reason'] for c in r['criteria'])+
                         '\nOnly these two fictional criteria were checked.',TOPICS)
        # Location is context, not proof that a request is out of domain.
        if re.search(r'\blipa\b',t):
            return reply('Do you mean a PGPC student living in Lipa, or a scholarship administered by Lipa City? Please clarify. Residency alone does not determine eligibility.', ['pgpc residency','external scholarship'])
        if t=='pgpc residency':
            return reply('That is relevant to PGPC guidance, but no verified residency policy is loaded. Please consult the scholarship office.',TOPICS)
        if t=='external scholarship':
            return reply('I cannot provide verified details for that external program. Please contact its administering office.',TOPICS)
        intent=self.classifier.predict(message)
        if intent:
            # Clear pending assessment when explicitly switching topics; do not parse it as a fact.
            if intent!='eligibility':
                state['pending']=None
            if intent=='greeting':
                return reply('Hello! This is the first Flask milestone. Choose a topic, or type demo for the fictional eligibility test.',TOPICS+['demo'])
            if intent=='availability':
                programs=self.kb.verified_programs()
                return reply('Verified programs: '+', '.join(p['name'] for p in programs) if programs else
                             'No verified scholarship programs have been loaded yet. Contact the scholarship office. You may try the separately labeled fictional demo.', ['demo']+TOPICS)
            program=self.demo if state['program_id']=='demo-a' else self.kb.get(state['program_id'])
            if not program:
                return reply('No verified scholarship has been selected or loaded. Real policy answers are unavailable. Type demo only if you want to try fictional test rules.', ['availability','demo'])
            if intent=='eligibility':
                if program['id']!='demo-a':
                    return reply('The manual collection flow for this program has not been configured yet.',TOPICS)
                state['facts']={};state['confirmed']=False;state['last_result']=None;state['pending']='year'
                return reply('FICTIONAL DEMO: What is your year level? Enter 1–9, for example 3. Use invented answers.', ['unknown','cancel'])
            info=self.kb.retrieve(program,intent)
            if info:
                return reply(info['answer'],TOPICS, source=info['source'], version=info['version'])
            return reply('No verified '+intent.replace('_',' ')+' information is available for this selection. Ask the scholarship office. I will not invent it.',TOPICS)
        if state['pending'] in {'year','grade'}:
            field=state['pending'];value=None
            if t not in {'unknown',"i’m not sure","i'm not sure"}:
                pattern=r'[1-9]' if field=='year' else r'(?:[0-9]{1,3})(?:\.[0-9]+)?%?'
                if not re.fullmatch(pattern,t):
                    return reply('Please enter '+('a year level 1–9.' if field=='year' else 'a percentage grade 0–100, such as 88. Do not convert another grade scale yourself.'),['unknown','cancel'])
                value=float(t.rstrip('%'))
                if field=='grade' and not 0<=value<=100:
                    return reply('Percentage must be from 0 to 100.', ['unknown','cancel'])
            if value is not None:
                state['facts'][field]={'value':value,'scale':'year_level' if field=='year' else 'percentage'}
            state['pending']='grade' if field=='year' else 'review'
            if field=='year':
                return reply('What is your average on a 0–100 percentage scale? If you have a different scale, choose unknown.', ['unknown','cancel'])
            lines=[k+': '+str(state['facts'].get(k,{}).get('value','Not provided')) for k in ['year','grade']]
            return reply('Review your fictional answers:\n'+'\n'.join(lines)+'\nGrade uses the percentage scale. Confirm before evaluation.', ['confirm','eligibility','cancel'])
        if state['pending']=='review':
            return reply('Please confirm, restart eligibility to change answers, or cancel.', ['confirm','eligibility','cancel'])
        return reply('I cannot reliably understand this phrasing yet: the group-trained intent model is not installed. Choose a topic below. Unknown requests are not automatically treated as out of scope.',TOPICS)
