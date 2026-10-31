"""Info Retrieval: reads the versioned JSON knowledge base and returns verified answers."""
import json
from pathlib import Path


class KnowledgeBase:
    def __init__(self, path, demo=None):
        self.data = json.loads(Path(path).read_text(encoding='utf-8'))
        self.demo = demo

    def verified_programs(self):
        return [p for p in self.data.get('programs', []) if p.get('verified') is True and p.get('source')]

    def applicable_programs(self):
        """Verified programs PGPC students can apply to (shown for 'availability')."""
        return [p for p in self.verified_programs() if p.get('applicable_to_pgpc', True)]

    def get(self, program_id):
        if self.demo and program_id == self.demo['id']:
            return self.demo
        return next((p for p in self.verified_programs() if p['id'] == program_id), None)

    def find_in_text(self, text):
        """Return the program whose name or alias appears in the student's message."""
        lowered = text.lower()
        candidates = self.verified_programs() + ([self.demo] if self.demo else [])
        best, best_len = None, 0
        for program in candidates:
            for name in [program['name']] + program.get('aliases', []):
                n = name.lower()
                if n and n in lowered and len(n) > best_len:
                    best, best_len = program, len(n)
        return best

    def public_list(self):
        """Programs for the Scholarships page: no personal data, only verified records."""
        def item(p):
            return {'name': p['name'], 'type': p.get('type'), 'source': p.get('source'),
                    'last_verified': p.get('last_verified'),
                    'reason': p.get('not_applicable_reason') if p.get('applicable_to_pgpc') is False else None}
        open_programs = self.applicable_programs()
        return {'open': [item(p) for p in open_programs],
                'not_open': [item(p) for p in self.verified_programs() if p not in open_programs]}

    @staticmethod
    def source_line(program):
        if not program.get('source'):
            return None
        verified = program.get('last_verified')
        return program['source'] + (f' (last verified {verified})' if verified else '')

    def retrieve(self, program, intent):
        """Answer an info question from the program record, or None if not available."""
        if intent == 'requirements':
            items = program.get('requirements') or []
            answer = '\n'.join(f'{i}. {d}' for i, d in enumerate(items, 1)) if items else None
        elif intent == 'deadline':
            answer = program.get('deadline')
        elif intent == 'application_procedure':
            answer = program.get('procedure')
        elif intent == 'general_info':
            parts = [program.get('description'), ('Benefits: ' + program['benefits']) if program.get('benefits') else None]
            office = program.get('office') or {}
            if office:
                parts.append('Office: ' + '; '.join(v for v in [office.get('address'), office.get('hours'), office.get('contact')] if v))
            answer = '\n'.join(p for p in parts if p) or None
        else:
            answer = None
        if not answer:
            return None
        return {'answer': answer, 'source': self.source_line(program), 'version': program.get('version')}
