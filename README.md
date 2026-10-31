# ASKOLAR (Development build v0.3)

ASKOLAR: An Expert System-Based Scholarship Information and Guidance Chatbot for PGPC Students.
Group 3 · CS 312 (Software Engineering I) and CSE 103 (Intelligent Systems).

Local Flask web app. The intent classifier, the language identifier and the expert system are trained or built by the group and run on this computer. No external AI, no online OCR and no user accounts (SRS v1.0 scope, NFR-09).

## Run on Windows

Open PowerShell in this folder (where `app.py` is). Python 3.13 and Tesseract OCR (`D:\Programming\Tesseract-OCR`) must be installed.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe training\export_from_excel.py "path\to\ASKOLAR.xlsx"
.\.venv\Scripts\python.exe training\train_intent.py
.\.venv\Scripts\python.exe training\train_language.py
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in Chrome or Edge. Ctrl+C stops the server. Installing needs internet once; running does not.

**Show it on a real phone (same Wi-Fi):** run `.\.venv\Scripts\python.exe -c "from askolar import create_app; create_app().run(host='0.0.0.0', port=5000)"`, find the laptop's IPv4 address with `ipconfig`, then open `http://<that address>:5000` on the phone. Allow Python through Windows Firewall (Private network) if asked.

**Run the tests:** `.\.venv\Scripts\python.exe -m unittest discover -s tests`

## Train the models (Rapio)

1. Review the Excel file (sheet "Training Questions"): Review status = Approved, Edited or Remove.
2. Export: `training\export_from_excel.py "path\to\ASKOLAR.xlsx"` → `training/intent_dataset.csv`.
3. Intent model: `training\train_intent.py --reviewed-only` (rows marked Remove are never used).
   To test on real student questions: add `--test-contributor "Student survey"`.
4. Language identifier: `training\train_language.py` (uses the Language column).
5. Results: `training/results.md`, `training/results.json`, `training/language_results.md`. Copy them into the Test Plan (M-01, M-02) and the IEEE paper. Report only the final run.
6. Models are saved to `models/` (not committed; rebuild them with the scripts). Restart `app.py` to load them.

Intent model: TF-IDF (word 1–2-grams + character 2–4-grams) → Logistic Regression; 80/20 split, seed 42, paraphrase groups kept in one split; final model refit on all questions; below 0.40 confidence → clarification.
Language identifier: TF-IDF character 2–4-grams → Logistic Regression. Messages with only English or only Filipino common words are decided by a word list; mixed messages by the model.

## Try it

| Type | What happens |
|---|---|
| `Hi po` | Greeting “Hello, iskolar!” (rule, not an intent) |
| `Hi po, ano ang requirements ng Vidal?` | Greeting is skipped; requirements answered in Filipino with source |
| `What scholarships are open?` | English reply: Vidal and Mendoza are open; San Juan LYDO is not open to PGPC |
| `Mendoza` → `eligibility` → `I agree` → `Padre Garcia, Batangas` → `1.55` → `23` → `confirm` → `why` | Rule check with MET/UNMET reasons, notes and disclaimer |
| `Magkano ang allowance?` | Benefit amounts are not given (out of scope) |
| `Paano magluto ng adobo?` | Out-of-scope reply |
| `taga Lipa ako` | Clarification, not rejection |
| `demo` → `eligibility` → … | Fictional rules: year level ≥ 2 and GWA ≤ 2.25 |
| Scholarships (sidebar) | List of verified programs from the knowledge base |

## Project structure (System Design v0.3, Figure 1)

| Path | Component |
|---|---|
| `askolar/services/conversation.py` | Conversation Manager (Facade): routing, consent, fact questions, review, language |
| `askolar/services/intent.py` | Intent Classifier (7 intents) |
| `askolar/services/language.py` | Language Identifier (English / Filipino / Taglish) |
| `askolar/services/smalltalk.py` | Greeting, thanks, goodbye rules; benefit-amount check |
| `askolar/services/knowledge.py` | Info Retrieval from the knowledge base |
| `askolar/services/expert.py` | Expert System: IF–THEN rules, MET / UNMET / UNRESOLVED |
| `askolar/services/facts.py` | The 5 eligibility facts and answer checking |
| `askolar/services/ocr.py` | OCR Service (Adapter) using local Tesseract |
| `askolar/services/composer.py` | Response Composer: builds every reply |
| `askolar/services/messages.py` | All fixed replies in English and Filipino |
| `data/knowledge_base.json` | Verified programs and rules (schema v2) |
| `training/` | Dataset export and training scripts |

See `FILES_EXPLAINED.md` for a simple explanation of each file (for the code walkthrough).

## Privacy (RA 10173)

No login. Answers stay in a temporary in-memory session and are deleted on New chat or after 30 minutes of inactivity. Uploaded images are deleted right after OCR. Do not commit student data, survey CSV files or grade report images to GitHub.
