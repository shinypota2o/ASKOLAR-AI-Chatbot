"""Intent Classifier: predicts the type of question with the group-trained model.

The model (TF-IDF + Logistic Regression) is trained by training/train_intent.py and saved
to models/intent_model.joblib. Greetings are handled by services/smalltalk.py.
Exact button commands (e.g., "availability") are mapped
directly so the suggestion buttons always work. If no trained model is present, only these
commands are understood and every other message gets a clarification question.
"""
from pathlib import Path

COMMANDS = {
    'availability': {'availability', 'scholarships', 'browse scholarships'},
    'requirements': {'requirements', 'documents'},
    'eligibility': {'eligibility', 'check eligibility', 'check my eligibility'},
    'deadline': {'deadline'},
    'application_procedure': {'application procedure', 'application steps'},
    'general_info': {'general information', 'general info'},
}


class IntentClassifier:
    def __init__(self, model_path=None):
        self.model = None
        self.threshold = 0.40
        self.mode = 'commands_only_model_not_trained'
        if model_path and Path(model_path).exists():
            import joblib  # loaded only when a trained model exists
            bundle = joblib.load(model_path)
            self.model = bundle['pipeline']
            self.threshold = bundle.get('threshold', self.threshold)
            self.mode = f'trained_model ({bundle.get("trained_on", "?")} questions, {bundle.get("created", "?")})'

    @staticmethod
    def _command(text):
        normalized = text.strip().lower().rstrip('?!.,')
        for label, phrases in COMMANDS.items():
            if normalized in phrases:
                return label
        return None

    def predict(self, text):
        """Return (intent or None, confidence). None means: ask the student to clarify."""
        command = self._command(text)
        if command:
            return command, 1.0
        if self.model is None:
            return None, 0.0
        probabilities = self.model.predict_proba([text])[0]
        best = probabilities.argmax()
        confidence = float(probabilities[best])
        label = self.model.classes_[best]
        return (label, confidence) if confidence >= self.threshold else (None, confidence)
