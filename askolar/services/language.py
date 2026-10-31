"""Language Identifier: decides whether a message is English, Filipino or Taglish,
so ASKOLAR can reply in the student's language (English replies for English,
Filipino replies for Filipino and Taglish).

It uses the group-trained model in models/language_model.joblib (TF-IDF character
n-grams + Logistic Regression, trained by training/train_language.py on the
Language column of our intent dataset). Without the model, or for very short
messages, a small word list is used instead.
"""
import re
from pathlib import Path

FILIPINO_WORDS = {
    'ang', 'ng', 'nang', 'mga', 'sa', 'na', 'po', 'opo', 'ba', 'ko', 'ako', 'mo', 'ka', 'kami', 'namin', 'natin',
    'tayo', 'siya', 'ito', 'iyan', 'yan', 'yung', 'iyong', 'nito', 'dito', 'doon', 'ano', 'anong', 'paano', 'pano',
    'kailan', 'kelan', 'saan', 'sino', 'bakit', 'ilan', 'magkano', 'pwede', 'puwede', 'pede', 'kailangan', 'kelangan',
    'may', 'meron', 'mayroon', 'wala', 'walang', 'lang', 'lamang', 'naman', 'din', 'rin', 'pa', 'nga', 'kasi', 'kung',
    'para', 'pag', 'kapag', 'hindi', 'di', 'oo', 'sige', 'salamat', 'kumusta', 'kamusta', 'hanggang', 'bukas', 'pasok',
    'ipapasa', 'ipasa', 'magpasa', 'mag', 'nag', 'ga', 'eh', 'ay', 'at', 'o', 'ni', 'kay', 'ko', 'yun', 'iyon', 'aking',
    'ako', 'akin', 'atin', 'amin', 'kanila', 'sila', 'nila', 'niya', 'ninyo', 'kayo', 'gusto', 'alam', 'tanong',
}
ENGLISH_WORDS = {
    'the', 'is', 'are', 'was', 'what', 'which', 'how', 'when', 'where', 'who', 'why', 'can', 'could', 'do', 'does',
    'did', 'i', 'my', 'me', 'you', 'your', 'we', 'our', 'for', 'of', 'to', 'a', 'an', 'and', 'or', 'if', 'there',
    'this', 'that', 'it', 'am', 'be', 'have', 'has', 'need', 'apply', 'submit', 'still', 'open', 'any', 'until',
    'with', 'about', 'please', 'should', 'will', 'qualify', 'qualified', 'eligible', 'want', 'know', 'tell',
}
LANGUAGES = ('English', 'Filipino', 'Taglish')


def _words(text):
    return re.findall(r"[a-zñ']+", text.lower())


def word_list_language(text):
    """Simple fallback: count common Filipino and English words."""
    words = _words(text)
    fil = sum(w in FILIPINO_WORDS for w in words)
    eng = sum(w in ENGLISH_WORDS for w in words)
    if fil == 0 and eng == 0:
        return None
    if fil and eng:
        return 'Taglish'
    return 'Filipino' if fil else 'English'


class LanguageIdentifier:
    def __init__(self, model_path=None):
        self.model = None
        self.mode = 'word_list'
        if model_path and Path(model_path).exists():
            import joblib
            bundle = joblib.load(model_path)
            self.model = bundle['pipeline']
            self.mode = f'trained_model ({bundle.get("trained_on", "?")} questions)'

    def detect(self, text):
        """Return 'English', 'Filipino', 'Taglish', or None when the message is too short to tell."""
        words = _words(text)
        if len(words) < 2:
            return None  # e.g., "2.0", "oo", "confirm": keep the language already in use
        simple = word_list_language(text)
        # Clear cases (only English or only Filipino function words) are trusted;
        # the trained model decides mixed or unclear messages.
        if simple in ('English', 'Filipino') or self.model is None or len(words) < 3:
            return simple
        return str(self.model.predict([text])[0])


def reply_language(detected):
    """English questions get English replies; Filipino and Taglish get Filipino replies."""
    if detected is None:
        return None
    return 'en' if detected == 'English' else 'fil'
