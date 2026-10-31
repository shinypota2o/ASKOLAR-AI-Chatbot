# Changes

## v0.3 (31 Oct 2026) — professor's UI feedback + language replies

| Area | Change | Docs to update (final) |
|---|---|---|
| UI | Larger text (16 px chat), PGPC logo (sidebar, replies, tab icon), ☀️/🌙 theme icon, sidebar tagline removed | System Design screens; SRS NFR-10 |
| UI | Start screen shows only “How can I help you today?” + 6 topic buttons (chatbot style); “Hello, iskolar!” is now a reply | System Design |
| UI | Removed: “A next step starts with a question”, “Explore scholarships…”, development badge, Mobile view button (responsive on real phones) | System Design |
| UI | Typing indicator, source card under answers, 📎 upload button shown only for GWA/units questions, privacy footer | FR-02, FR-13 |
| Language | Auto / EN / FIL toggle; UI text in English or Filipino; replies follow the student’s language (Filipino/Taglish → Filipino) | New FR-17; TC-29, TC-30 |
| AI | Language Identifier trained on the Language column (training/train_language.py) | Paper (AI design); Test Plan |
| Conversation | Greetings, thanks, goodbyes handled by rules (with “po”); “Hi po, + question” answers the question | TC-31; System Design |
| Conversation | Benefit amounts are never given (SRS v1.0 scope); “Magkano ang tuition fee?” stays out of scope | — |
| Conversation | Renewals, application status and payout schedules get a referral reply (rule, not an intent) | SRS scope; paper limitations; new test case |
| Conversation | Lipa clarification is skipped when the message is out of scope | TC-27 |
| Scholarships page | Lists verified programs from the knowledge base with source and last verified date (`/api/programs`) | FR-02; System Design |
| Knowledge base | Added Office of BM Melvin Vidal and Bokal Marcus Mendoza (verified, with notes); GVSR stored but hidden until OSA permission | Data Summary |
| OCR | Removes table lines and crops the card; reads GWA and total units only (year level is not taken from old cards); needs opencv-python-headless | FR-13, M-03 (see TEST_RESULTS.md) |
| Training | Review status Approved/Edited/Remove; `--test-contributor` to test on real student questions | Test Plan M-01 |
| Tests | 45 tests (was 32) | Test Plan |
| Requirements | Added pytesseract, Pillow and opencv-python-headless; tested on Python 3.13 | Test Plan environment |

## v0.2 (29 Oct 2026)

| Area | Change | Requirement |
|---|---|---|
| Intent model | New `training/train_intent.py`: TF-IDF + Logistic Regression, grouped 80/20 split, accuracy/precision/recall/F1/confusion matrix/per-language accuracy, saves model | FR-05, NFR-01, M-01, M-02 |
| Intent model | New `training/export_from_excel.py` (Excel → CSV) and `training/intent_dataset.csv` (115 questions, 105 still drafts for review) | SRS 5.3 |
| Intent Classifier | Loads the trained model; confidence below 0.40 → clarification; button commands still work | FR-05, FR-06 |
| Expert System | Supports `>=`, `<=` (GWA: lower is better), `in` (residency); 5 standard fact names; PGPC school location fixed to Padre Garcia | FR-10, FR-11, NFR-11 |
| Expert System | Programs that every PGPC student fails (e.g., school must be in San Juan) are explained right away without asking personal facts | Proportionality (RA 10173) |
| Conversation | Privacy notice + consent before any fact; declining collects nothing | FR-03 |
| Conversation | Facts asked one by one from the program's rules; review and confirm before evaluation; "why" explanation | FR-10, FR-12 |
| Conversation | Out-of-scope reply; unclear → clarification; program chosen by name; follow-ups keep the program | FR-04, FR-06, FR-07 |
| Info Retrieval | Answers show source + last verified date; "not available" when missing | FR-02, FR-08, FR-09 |
| Knowledge base | Schema v2; San Juan LYDO record from the expert survey, marked not applicable to PGPC students | SRS 5.2 |
| Response Composer | All reply wording (info + source, availability, fact questions, review, result, why) moved from the Conversation Manager into the Response Composer, matching Figure 1 steps 5–6 | System Design v0.3 |
| Demo | Fictional demo now uses year level ≥ 2 and GWA ≤ 2.25 | — |
| UI | About/Scholarships text and footer updated | — |
| Tests | 27 tests (was 14), named with Test Plan IDs | Test Plan v1.0 |
| Code style | Rewritten files follow PEP 8 (Coding Standards 2.2) | — |

Not changed in the first v0.2 build: session handling, CSRF protection, UI design. The local OCR adapter (Tesseract) was added later in the v0.2 working copy.
