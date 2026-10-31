"""The five eligibility facts ASKOLAR may ask for, and how student answers are parsed.

Only facts that a program's rules need are ever asked (SRS FR-10, proportionality).
School location is not asked: it is fixed for every PGPC student.
"""
import re

PGPC_MUNICIPALITY = 'Padre Garcia, Batangas'

# Facts that are the same for every PGPC student, so they are never asked.
FIXED_FACTS = {
    'school_municipality': {'value': PGPC_MUNICIPALITY, 'scale': 'municipality'},
}

UNKNOWN_WORDS = {'unknown', 'not sure', "i'm not sure", 'i’m not sure', 'hindi ko alam', 'di ko alam', 'skip'}


class FactError(ValueError):
    """Raised when an answer cannot be used; the message is shown to the student.

    The key points to services/messages.py so the reply can be English or Filipino.
    """

    def __init__(self, key):
        from .messages import MESSAGES
        self.key = key
        super().__init__(MESSAGES[key]['en'])


def _number(text):
    cleaned = text.replace(',', '').replace('₱', '').replace('php', '').strip()
    if not re.fullmatch(r'\d+(\.\d+)?', cleaned):
        raise FactError('err_number')
    return float(cleaned)


def parse_year_level(text):
    value = _number(text)
    if value != int(value) or not 1 <= value <= 5:
        raise FactError('err_year')
    return int(value)


def parse_gwa(text):
    value = _number(text)
    if not 1.0 <= value <= 5.0:
        raise FactError('err_gwa')
    return round(value, 2)


def parse_family_income(text):
    value = _number(text)
    if value < 0:
        raise FactError('err_income')
    return value


def parse_units(text):
    value = _number(text)
    if value != int(value) or not 0 <= value <= 40:
        raise FactError('err_units')
    return int(value)


def normalize_place(text):
    """'San Juan, Batangas' and 'san juan' both become 'san juan'."""
    text = text.lower().replace('city of', '').replace('municipality of', '')
    text = re.sub(r'[^a-z\s,]', ' ', text)
    first = re.sub(r'\s+', ' ', text.split(',')[0]).strip()
    if first.endswith(' batangas'):  # "san juan batangas" -> "san juan"; keeps "batangas city"
        first = first[:-len(' batangas')]
    return first


def parse_residency(text):
    place = text.strip()
    if len(place) < 3 or re.fullmatch(r'[\d\s.,]+', place):
        raise FactError('err_residency')
    return place.title()


FACTS = {
    'year_level': {
        'label': 'College year level',
        'question': 'What is your current college year level? Enter a number from 1 to 5, e.g., 3.',
        'scale': 'year_level',
        'parse': parse_year_level,
    },
    'gwa': {
        'label': 'GWA',
        'question': 'What is your latest GWA on the 1.00–5.00 scale (1.00 is the highest)? e.g., 1.75',
        'scale': 'gwa_1_to_5',
        'parse': parse_gwa,
    },
    'family_income': {
        'label': 'Annual family income (PHP)',
        'question': 'What is your family’s total ANNUAL income in pesos? e.g., 180000',
        'scale': 'php_per_year',
        'parse': parse_family_income,
    },
    'residency': {
        'label': 'Municipality / city of residence',
        'question': 'Which municipality or city do you live in? e.g., Padre Garcia, Batangas',
        'scale': 'municipality',
        'parse': parse_residency,
    },
    'units': {
        'label': 'Enrolled units this semester',
        'question': 'How many academic units are you enrolled in this semester? e.g., 21',
        'scale': 'units',
        'parse': parse_units,
    },
}


def is_unknown(text):
    return text.strip().lower().rstrip('.!') in UNKNOWN_WORDS


def parse_fact(name, text):
    """Return a fact dict, or a fact with value None if the student does not know."""
    spec = FACTS[name]
    if is_unknown(text):
        return {'value': None, 'scale': spec['scale']}
    return {'value': spec['parse'](text), 'scale': spec['scale']}
