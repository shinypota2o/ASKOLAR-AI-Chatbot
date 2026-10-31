"""Fixed ASKOLAR replies in English ('en') and Filipino ('fil').

Taglish questions get the Filipino replies, which keep common English terms
(requirements, GWA, units) the way PGPC students chat. Program details from the
knowledge base stay in the wording of their official source.
"""

MESSAGES = {
    # ---------- general ----------
    'greeting': {
        'en': 'Hello, iskolar! 👋 I can help with PGPC scholarship information and preliminary eligibility checks. What would you like to know?',
        'fil': 'Hello, iskolar! 👋 Matutulungan kita sa impormasyon tungkol sa scholarships para sa PGPC students at sa paunang eligibility check. Ano ang gusto mong malaman?',
    },
    'thanks': {
        'en': 'You’re welcome! Is there anything else you would like to know?',
        'fil': 'Walang anuman! May iba ka pa bang gustong malaman?',
    },
    'bye': {
        'en': 'Goodbye, and good luck with your application! Click New chat to delete this conversation.',
        'fil': 'Paalam, at good luck sa application mo! I-click ang Bagong chat para burahin ang usapang ito.',
    },
    'not_understood': {
        'en': 'Sorry, I did not understand that. What would you like to know? You can choose a topic below or rephrase your question.',
        'fil': 'Pasensya, hindi ko naintindihan. Ano ang gusto mong malaman? Pumili ng topic sa ibaba o itanong ulit sa ibang paraan.',
    },
    'out_of_scope': {
        'en': 'I can only answer questions about scholarships and educational assistance for PGPC students. Try asking about available scholarships, requirements, deadlines or eligibility.',
        'fil': 'Scholarships at educational assistance para sa PGPC students lang ang kaya kong sagutin. Subukang magtanong tungkol sa available na scholarships, requirements, deadline o eligibility.',
    },
    'amounts': {
        'en': 'ASKOLAR does not provide benefit or allowance amounts, because they can change. Please ask the scholarship office.',
        'fil': 'Hindi nagbibigay ang ASKOLAR ng halaga ng benefits o allowance, dahil puwede itong magbago. Pakitanong sa scholarship office.',
    },
    'unsupported': {
        'en': 'ASKOLAR does not cover scholarship renewals, application status, or payout schedules yet. Please ask the scholarship office.',
        'fil': 'Hindi pa sakop ng ASKOLAR ang renewal ng scholarship, status ng application, at schedule ng payout. Pakitanong sa scholarship office.',
    },
    'office_line': {'en': 'Office of {name}: {office}', 'fil': 'Office ng {name}: {office}'},
    'disclaimer': {
        'en': 'This is preliminary guidance only, not approval. The scholarship office makes the final decision.',
        'fil': 'Paunang gabay lamang ito, hindi approval. Ang scholarship office pa rin ang magdedesisyon.',
    },
    # ---------- demo, cancel, location ----------
    'demo_selected': {
        'en': 'FICTIONAL DEMO selected. These are not PGPC policies. Type eligibility to try the rules.',
        'fil': 'FICTIONAL DEMO ang napili. Hindi ito totoong PGPC policy. I-type ang eligibility para subukan ang rules.',
    },
    'cancelled': {
        'en': 'Check cancelled. Your temporary answers were cleared.',
        'fil': 'Kinansela ang check. Nabura na ang mga pansamantalang sagot mo.',
    },
    'lipa_clarify': {
        'en': 'Do you mean a PGPC student living in Lipa, or a scholarship offered by Lipa City? Please clarify. Residency alone does not decide eligibility.',
        'fil': 'Ang ibig mo bang sabihin ay PGPC student na nakatira sa Lipa, o scholarship na galing sa Lipa City? Pakilinaw. Hindi lang tirahan ang batayan ng eligibility.',
    },
    'pgpc_residency': {
        'en': 'Residency can matter for local government programs. Ask about a specific program, or type availability.',
        'fil': 'Mahalaga ang tirahan sa mga programa ng LGU. Magtanong tungkol sa isang program, o i-type ang availability.',
    },
    'external': {
        'en': 'I can only give verified details for programs in ASKOLAR’s knowledge base. Please contact the program’s office.',
        'fil': 'Verified na detalye lang ng mga program sa knowledge base ng ASKOLAR ang kaya kong ibigay. Pakikontak ang office ng program.',
    },
    # ---------- programs ----------
    'need_program_none': {
        'en': 'No verified programs open to PGPC students are loaded yet, so I cannot answer that. Please ask the Office of Student Affairs, or type demo to try the fictional example.',
        'fil': 'Wala pang verified na program para sa PGPC students, kaya hindi ko pa ito masasagot. Pakitanong sa Office of Student Affairs, o i-type ang demo para subukan ang fictional na halimbawa.',
    },
    'which_program': {'en': 'Which scholarship do you mean?', 'fil': 'Aling scholarship ang tinutukoy mo?'},
    'avail_none': {
        'en': 'No verified scholarship programs open to PGPC students have been loaded yet. Please ask the Office of Student Affairs. You may also try the separately labeled fictional demo.',
        'fil': 'Wala pang verified na scholarship para sa PGPC students. Pakitanong sa Office of Student Affairs. Puwede mo ring subukan ang fictional demo.',
    },
    'avail_head': {'en': 'Verified programs open to PGPC students:', 'fil': 'Mga verified na program para sa PGPC students:'},
    'avail_choose': {'en': 'Choose one to learn more.', 'fil': 'Pumili ng isa para malaman ang detalye.'},
    'avail_others': {
        'en': 'Also in ASKOLAR but NOT open to PGPC students: {names}. Ask about it to see why.',
        'fil': 'Nasa ASKOLAR din pero HINDI para sa PGPC students: {names}. Itanong ito para malaman kung bakit.',
    },
    'info_missing': {
        'en': 'No verified {topic} information is available for {name}. Please ask the scholarship office. I will not invent it.',
        'fil': 'Walang verified na impormasyon tungkol sa {topic} ng {name}. Pakitanong sa scholarship office. Hindi ako manghuhula.',
    },
    'requirements_head': {'en': 'Requirements for {name}:', 'fil': 'Requirements para sa {name}:'},
    'office': {'en': 'Office', 'fil': 'Office'},
    'note': {'en': 'Note', 'fil': 'Paalala'},
    'notes_head': {'en': 'Also required (the office checks these):', 'fil': 'Kailangan din (ang office ang magche-check nito):'},
    'source': {'en': 'Source', 'fil': 'Source'},
    'last_verified': {'en': 'last verified {date}', 'fil': 'huling na-verify {date}'},
    # ---------- eligibility ----------
    'privacy_notice': {
        'en': 'Privacy notice: to check eligibility, ASKOLAR will ask only for the facts this program’s rules need. Your answers are kept only in this temporary session, used only for preliminary guidance, and deleted when you click New chat or after 30 minutes of inactivity (Data Privacy Act of 2012, RA 10173). Do you agree?',
        'fil': 'Privacy notice: para sa eligibility check, itatanong lang ng ASKOLAR ang mga impormasyong kailangan ng rules ng program na ito. Nasa pansamantalang session lang ang mga sagot mo, gagamitin lang para sa paunang gabay, at buburahin kapag nag-click ka ng Bagong chat o pagkalipas ng 30 minutong walang galaw (Data Privacy Act of 2012, RA 10173). Pumapayag ka ba?',
    },
    'consent_declined': {
        'en': 'Okay, no personal information will be collected. You can still ask about scholarships.',
        'fil': 'Sige, walang personal na impormasyong kukunin. Puwede ka pa ring magtanong tungkol sa scholarships.',
    },
    'fictional': {'en': 'FICTIONAL DEMO: ', 'fil': 'FICTIONAL DEMO: '},
    'unknown_hint': {'en': ' (Type unknown if you are not sure.)', 'fil': ' (I-type ang unknown kung hindi sigurado.)'},
    'upload_hint': {'en': ' You may also upload a photo of your class card or grade report.',
                    'fil': ' Puwede ka ring mag-upload ng picture ng class card o grade report mo.'},
    'upload_use_button': {
        'en': 'Please use the 📎 button to choose a photo of your class card or grade report, or type your answer.',
        'fil': 'Pindutin ang 📎 para pumili ng picture ng class card o grade report mo, o i-type na lang ang sagot.',
    },
    'or_unknown': {'en': ' Or type unknown.', 'fil': ' O i-type ang unknown.'},
    'review_head': {'en': 'Please review your answers:', 'fil': 'Pakitingnan ang mga sagot mo:'},
    'review_tail': {'en': 'Confirm before I check the rules.', 'fil': 'I-confirm muna bago ko i-check ang rules.'},
    'review_prompt': {'en': 'Please confirm your answers, type eligibility to answer again, or cancel.',
                      'fil': 'Pakiconfirm ang mga sagot mo, i-type ang eligibility para sumagot ulit, o cancel.'},
    'not_provided': {'en': 'Not provided', 'fil': 'Walang sagot'},
    'from_document': {'en': ' (from document)', 'fil': ' (mula sa document)'},
    'why_head': {'en': 'Here is why:', 'fil': 'Ito ang dahilan:'},
    'only_listed': {'en': 'Only the listed criteria were checked.', 'fil': 'Ang mga nakalistang criteria lang ang na-check.'},
    'overall_POTENTIALLY_MEETS_LISTED_CRITERIA': {'en': 'You potentially meet the listed criteria.',
                                                  'fil': 'Posibleng pasok ka sa mga nakalistang criteria.'},
    'overall_LISTED_CRITERIA_NOT_MET': {'en': 'You do not meet one or more listed criteria.',
                                        'fil': 'Hindi ka pasok sa isa o higit pang nakalistang criteria.'},
    'overall_NEEDS_MORE_INFORMATION': {'en': 'More information is needed to check all criteria.',
                                       'fil': 'Kailangan pa ng impormasyon para ma-check ang lahat ng criteria.'},
    'overall_INSUFFICIENT_POLICY': {'en': 'The eligibility rules for this program are not complete yet, so no result can be given.',
                                    'fil': 'Hindi pa kumpleto ang eligibility rules ng program na ito, kaya wala pang resulta.'},
    'ask_office': {'en': ' Please ask the scholarship office.', 'fil': ' Pakitanong sa scholarship office.'},
    'status_MET': {'en': 'MET', 'fil': 'PASOK (MET)'},
    'status_UNMET': {'en': 'UNMET', 'fil': 'HINDI PASOK (UNMET)'},
    'status_UNRESOLVED': {'en': 'UNRESOLVED', 'fil': 'HINDI PA MA-CHECK (UNRESOLVED)'},
    # ---------- rule reasons (expert system) ----------
    'reason_at_least': {'en': 'Your value is {value}; the rule requires at least {threshold}.',
                        'fil': 'Ang sagot mo ay {value}; kailangan ay hindi bababa sa {threshold}.'},
    'reason_at_most': {'en': 'Your value is {value}; the rule requires at most {threshold}.',
                       'fil': 'Ang sagot mo ay {value}; kailangan ay hindi hihigit sa {threshold}.'},
    'reason_accepted': {'en': 'Your value is {value}; accepted: {allowed}.',
                        'fil': 'Ang sagot mo ay {value}; tinatanggap: {allowed}.'},
    'reason_not_provided': {'en': 'This information was not provided.', 'fil': 'Hindi ito nasagot.'},
    'reason_scale': {'en': 'The value uses a different scale from the rule.', 'fil': 'Iba ang scale ng sagot sa rule.'},
    'reason_numeric': {'en': 'This rule needs a numeric value.', 'fil': 'Kailangan ng numero sa rule na ito.'},
    'reason_list': {'en': 'This rule needs a list of accepted values.', 'fil': 'Kailangan ng listahan ng tinatanggap na sagot.'},
    'reason_policy': {'en': 'This rule needs policy clarification from the scholarship office.',
                      'fil': 'Kailangang linawin ng scholarship office ang rule na ito.'},
    'reason_confirm': {'en': 'Your answers must be confirmed first.', 'fil': 'Kailangan munang i-confirm ang mga sagot mo.'},
    'reason_school': {'en': 'The school must be in {allowed}, but PGPC is in {pgpc}.',
                      'fil': 'Dapat nasa {allowed} ang school, pero ang PGPC ay nasa {pgpc}.'},
    # ---------- OCR ----------
    'ocr_head': {'en': 'I read these values from your document:', 'fil': 'Ito ang nabasa ko sa document mo:'},
    'ocr_tail': {
        'en': 'Please check them carefully. OCR can make mistakes, especially with handwriting. Use these values, or type your answers instead?\nThe uploaded file has already been deleted.',
        'fil': 'Pakitingnan nang mabuti. Puwedeng magkamali ang OCR, lalo na sa sulat-kamay. Gamitin ba ang mga ito, o i-type mo na lang?\nNabura na ang na-upload na file.',
    },
    'ocr_nothing': {
        'en': 'I could not read the needed values from the document (handwritten grades are often hard to read). The uploaded file has been deleted. Please type your answer instead.',
        'fil': 'Hindi ko nabasa ang mga kailangang value sa document (madalas mahirap basahin ang sulat-kamay). Nabura na ang na-upload na file. Pakitype na lang ang sagot mo.',
    },
    'ocr_no_file_kept': {'en': ' No file was kept.', 'fil': ' Walang file na itinago.'},
    # ---------- fact errors ----------
    'err_number': {'en': 'Please enter a number only.', 'fil': 'Numero lang ang ilagay.'},
    'err_year': {'en': 'Please enter your college year level as a whole number from 1 to 5.',
                 'fil': 'Ilagay ang year level mo bilang buong numero mula 1 hanggang 5.'},
    'err_gwa': {'en': 'Please enter your GWA on the 1.00–5.00 scale (1.00 is the highest).',
                'fil': 'Ilagay ang GWA mo sa 1.00–5.00 na scale (1.00 ang pinakamataas).'},
    'err_income': {'en': 'Income cannot be negative.', 'fil': 'Hindi puwedeng negative ang income.'},
    'err_units': {'en': 'Please enter the number of units you are enrolled in this semester (0–40).',
                  'fil': 'Ilagay ang bilang ng units mo ngayong semester (0–40).'},
    'err_residency': {'en': 'Please type the name of your municipality or city, e.g., “Padre Garcia, Batangas”.',
                      'fil': 'I-type ang pangalan ng bayan o city mo, hal. “Padre Garcia, Batangas”.'},
}

# Fact questions and labels (keys match services/facts.py).
FACT_TEXT = {
    'year_level': {
        'label': {'en': 'College year level', 'fil': 'Year level'},
        'question': {'en': 'What is your current college year level? Enter a number from 1 to 5, e.g., 3.',
                     'fil': 'Anong year level mo ngayon? Ilagay ang numero mula 1 hanggang 5, hal. 3.'},
    },
    'gwa': {
        'label': {'en': 'GWA', 'fil': 'GWA'},
        'question': {'en': 'What is your latest GWA on the 1.00–5.00 scale (1.00 is the highest)? e.g., 1.75',
                     'fil': 'Ano ang pinakabagong GWA mo sa 1.00–5.00 na scale (1.00 ang pinakamataas)? hal. 1.75'},
    },
    'family_income': {
        'label': {'en': 'Annual family income (PHP)', 'fil': 'Taunang kita ng pamilya (PHP)'},
        'question': {'en': 'What is your family’s total ANNUAL income in pesos? e.g., 180000',
                     'fil': 'Magkano ang kabuuang TAUNANG kita ng pamilya mo sa piso? hal. 180000'},
    },
    'residency': {
        'label': {'en': 'Municipality / city of residence', 'fil': 'Bayan / city na tinitirhan'},
        'question': {'en': 'Which municipality or city do you live in? e.g., Padre Garcia, Batangas',
                     'fil': 'Saang bayan o city ka nakatira? hal. Padre Garcia, Batangas'},
    },
    'units': {
        'label': {'en': 'Enrolled units this semester', 'fil': 'Units ngayong semester'},
        'question': {'en': 'How many academic units are you enrolled in this semester? e.g., 21',
                     'fil': 'Ilang units ang naka-enroll sa iyo ngayong semester? hal. 21'},
    },
}

TOPIC_NAMES = {
    'requirements': {'en': 'requirements', 'fil': 'requirements'},
    'deadline': {'en': 'deadline', 'fil': 'deadline'},
    'application_procedure': {'en': 'application procedure', 'fil': 'paraan ng pag-apply'},
    'general_info': {'en': 'general information', 'fil': 'pangkalahatang impormasyon'},
}


def lang_or_default(lang):
    return lang if lang in ('en', 'fil') else 'en'


def t(key, lang='en', **values):
    """Return the message for key in the given language, filled with values."""
    text = MESSAGES[key][lang_or_default(lang)]
    return text.format(**values) if values else text


def fact_label(field, lang='en'):
    return FACT_TEXT[field]['label'][lang_or_default(lang)]


def fact_question(field, lang='en'):
    return FACT_TEXT[field]['question'][lang_or_default(lang)]


def topic_name(intent, lang='en'):
    names = TOPIC_NAMES.get(intent)
    return names[lang_or_default(lang)] if names else intent.replace('_', ' ')
