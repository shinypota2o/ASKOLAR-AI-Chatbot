"""Explicit navigation commands only. No trained language model is bundled.
Replace predict with a locally loaded, group-trained pipeline after evaluation.
Do not claim these commands are machine learning.
"""
COMMANDS = {
    'availability': {'availability', 'scholarships', 'browse scholarships'},
    'requirements': {'requirements', 'documents'},
    'eligibility': {'eligibility', 'check eligibility', 'check my eligibility'},
    'deadline': {'deadline'},
    'application_procedure': {'application procedure', 'application steps'},
    'general_info': {'general information', 'general info'},
    'greeting': {'hi', 'hello', 'kumusta'},
}
class IntentClassifier:
    mode = 'commands_only_model_not_trained'
    def predict(self, text):
        normalized = text.strip().lower().rstrip('?!.,')
        for label, phrases in COMMANDS.items():
            if normalized in phrases:
                return label
        return None
