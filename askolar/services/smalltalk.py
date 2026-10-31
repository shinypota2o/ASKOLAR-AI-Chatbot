"""Greetings, thanks and goodbyes.

These are handled by simple rules in the Conversation Manager, not by the intent model,
so ASKOLAR keeps its 7 scholarship intents (SRS 5.3). "Hi po, ano ang requirements?"
is treated as a greeting plus a question: the greeting is removed and the question
goes on to the intent model.
"""
import re

GREETINGS = [
    'good morning', 'good afternoon', 'good evening', 'good day', 'magandang umaga', 'magandang hapon',
    'magandang gabi', 'magandang araw', 'hello', 'hellow', 'helo', 'hi', 'hii', 'hiii', 'hey', 'hai', 'kumusta',
    'kamusta', 'musta', 'yo',
]
THANKS = ['maraming salamat', 'thank you', 'thank u', 'thanks', 'thankyou', 'salamat', 'ty', 'tysm']
BYES = ['goodbye', 'good bye', 'bye', 'paalam', 'see you', 'babye']
FILLERS = r'(?:\s+(?:po|poo|opo|askolar|iskolar|there|ulit|again|everyone|so much|much|ha|ah|na|din|rin|ka))*'


def _normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[!?.,~😊🙂👋❤️💙]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _match(text, phrases):
    """Return the rest of the message after a leading phrase (plus fillers like 'po'), or None."""
    for phrase in sorted(phrases, key=len, reverse=True):
        m = re.match(rf'^{re.escape(phrase)}\b{FILLERS}\s*', text)
        if m:
            return text[m.end():].strip()
    return None


def classify(message):
    """Return (kind, rest): kind is 'greeting', 'thanks', 'bye' or None.

    rest is the question left after a greeting ('' when there is none).
    """
    text = _normalize(message)
    rest = _match(text, THANKS)
    if rest is not None and not rest:
        return 'thanks', ''
    rest = _match(text, BYES)
    if rest is not None and not rest:
        return 'bye', ''
    rest = _match(text, GREETINGS)
    if rest is not None:
        return 'greeting', rest
    return None, text


AMOUNT_PATTERN = re.compile(r'\b(magkano|how much|amount|halaga|ilang pera|gaano kalaki)\b', re.I)


def asks_amount(message):
    """Benefit amounts are out of scope (SRS v1.0 scope)."""
    return bool(AMOUNT_PATTERN.search(message))


UNSUPPORTED_PATTERN = re.compile(
    r'\b(renew\w*|ma-?renew|re-?apply\w* (?:after|for renewal)|payout|pay-?out|release (?:ng|of) (?:the )?(?:allowance|stipend|pera|cash)'
    r'|(?:ire-?release|irerelease|marerelease|ma-?release) (?:ang|yung|ba ang)? ?(?:allowance|stipend|pera|cash|assistance)'
    r'|kailan (?:po )?(?:ang )?(?:payout|release|bigayan|claim)|(?:application )?status (?:ng|of) (?:my |aking |ko )?application'
    r'|(?:officially )?accepted na (?:ba )?(?:po )?ako|approved na (?:ba )?(?:po )?(?:ako|application ko|ang application ko)|natanggap na ba ako'
    r'|stipend release|application status|status ng (?:application|scholarship))\b', re.I)


def asks_unsupported(message):
    """Renewals, application status and payout schedules are not covered (SRS scope, v0.3)."""
    return bool(UNSUPPORTED_PATTERN.search(message))

