# ASKOLAR Flask Starter v0.1

First implementation milestone based on ASKOLAR_Handwritten_Ready_Timeline_Design_Gantt_v1.3.pdf, System Design v0.3, pages 2–5. Local development only. Use invented test facts.

## What changed
The original blue UI now sends messages to Python through Flask. Python handles conversation context, information retrieval and a fictional two-rule eligibility flow. JavaScript only handles display and requests. This is a runnable foundation, not a complete final system.

## Run on Windows (Python 3.11 or 3.12 recommended for this starter)
Extract the ZIP first. Open PowerShell in this folder (where app.py is).

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in Chrome or Edge. Keep the terminal running. Ctrl+C stops it. No virtual-environment activation is needed. If `py` is unavailable, use your installed Python executable to create the environment. Dependency installation needs internet; runtime uses no online AI services.

Do not double-click templates/index.html: the UI requires the Flask server now.

## First trial (type each message separately)
1. `hello`
2. `availability` — should report no verified programs loaded.
3. `demo` — explicitly selects a FICTIONAL development fixture.
4. `eligibility`
5. `3`
6. `88`
7. `confirm` — Python returns an explained preliminary demo result.
8. `why`

Try `1` and `80` for unmet criteria, or `unknown` for missing data. Try `Lipa` for clarification. New chat clears the server-side facts and visible chat. Check themes and Mobile view too.

## Architecture mapping
- templates/index.html + static/: Web Chat UI.
- askolar/services/conversation.py: Conversation Manager (Facade).
- askolar/services/intent.py: classifier interface; currently explicit command matching ONLY.
- askolar/services/knowledge.py: Info Retrieval and versioned JSON access.
- askolar/services/expert.py: numeric rule evaluation with met/unmet/unresolved.
- askolar/services/ocr.py: OCR Adapter interface; not implemented, returns HTTP 501.
- askolar/services/composer.py: common response format.
- data/knowledge_base.json: empty verified knowledge base, maintained offline.
- data/demo_program.json: separate fictional test fixture, never an actual policy.
- askolar/__init__.py: routes, CSRF protection and isolated temporary sessions.

## Implemented vs pending
Implemented: Flask-to-UI requests and responses, command-based navigation, clarification fallback, session isolation, explicit reset, expiry cleanup, manual fictional eligibility collection, confirmation, rule explanations, theme/mobile controls and automated backend tests.

PENDING: group-trained TF-IDF + Logistic Regression model, reviewed multilingual dataset, real coordinator-verified policies, configurable collection for real scholarship fields, OCR extraction and upload/review screens, OCR accuracy evaluation, deployment hardening, comprehensive browser/accessibility/user testing and final results.

There is NO trained intent model in this ZIP. Natural questions outside explicit topic commands receive an honest clarification message. The interface in intent.py is where the evaluated local model will later be loaded. questions_template.csv is only a header template, not training data. Review labels, group near duplicates, and split train/test before fitting TF-IDF or Logistic Regression; do not claim dataset or model accuracy yet.

The attached v1.3 architecture uses JSON knowledge records and temporary sessions. It does not specify account registration/login or an account database. Those earlier account ideas are NOT implemented here; confirm a design update before adding them. A Supabase connection is not required to try this milestone.

## Data lifetime and limits
Personal demo facts exist only in isolated server memory, not in the cookie. The cookie contains a random session ID. No chat-message history is persisted server-side. New chat explicitly deletes that session. Sessions expire after 30 minutes of inactivity, with cleanup at the next request or within an additional 30-second background sweep. Stopping the process clears all records. Closing the tab alone does NOT immediately notify the server. Only theme preference is stored in browser localStorage.

The starter runs one local process and is not suitable for a public multi-worker deployment. It has no user authentication or verified PGPC access control. The local HTTP cookie is not marked Secure; hosted deployment requires HTTPS, secure-cookie configuration, rate limits, deployment review and appropriate session storage. No legal compliance or production security certification is claimed. No upload files are accepted or retained by the OCR placeholder. Raw grades/income must not be added to logs or Git.

## Tests
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Tests cover API validation, session isolation/reset/expiry, confirmation, boundaries, missing data, scale mismatch, scope clarification, empty knowledge/rules and unavailable OCR. These are implementation checks, not measured chatbot or OCR accuracy.

## Next work, in small steps
1. Run the exact demo above and check the interface locally.
2. Have the group verify the first scholarship source and fill its policy record; review before activation.
3. Prepare and review original Filipino/English/Taglish questions. Train and evaluate the classifier separately; integrate its saved local pipeline.
4. Add supported OCR extraction and confirmation after agreeing the document format and dependency; measure raw field accuracy before correction.
5. Extend tests and conduct usability/acceptance review before deployment.

To edit: start with services/conversation.py for flow, services/expert.py for rule semantics and static/style.css for appearance. Every member should understand their assigned component and record contributions.
