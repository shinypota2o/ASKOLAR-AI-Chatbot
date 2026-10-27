import json
from pathlib import Path
class KnowledgeBase:
    def __init__(self, path):
        self.data = json.loads(Path(path).read_text(encoding='utf-8'))
    def verified_programs(self):
        return [p for p in self.data['programs'] if p.get('verified') is True and p.get('source')]
    def get(self, program_id):
        return next((p for p in self.verified_programs() if p['id'] == program_id), None)
    def retrieve(self, program, intent):
        field = {'requirements':'requirements', 'deadline':'deadline',
                 'application_procedure':'procedure', 'general_info':'description'}.get(intent)
        value = program.get(field) if field else None
        if not value:
            return None
        return {'answer': value, 'source':program['source'], 'version':program['version']}
