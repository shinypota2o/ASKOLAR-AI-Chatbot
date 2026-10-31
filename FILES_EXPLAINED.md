# ASKOLAR — Simpleng paliwanag ng bawat file (para sa code walkthrough)

Basahin ito bago ang defense. Puwedeng tanungin ng panel ang **kahit sinong member** (Term Guide 2.2).

## Daloy ng isang tanong (System Design Figure 1)

```
Student types → app.js → /api/chat (__init__.py)
   → Conversation Manager (conversation.py)
       1. Language Identifier (language.py): English, Filipino o Taglish?
       2. Small talk (smalltalk.py): bati, salamat, paalam?
       3. Intent Classifier (intent.py): anong klase ng tanong (7 intents)?
       4a. Info Retrieval (knowledge.py): kunin ang sagot sa knowledge base
       4b. Expert System (expert.py + facts.py): i-check ang IF–THEN rules
       4c. OCR (ocr.py): basahin ang picture ng class card (optional)
   → Response Composer (composer.py + messages.py): buuin ang sagot sa tamang language
→ app.js: ipakita ang sagot, source, at buttons
```

## Bawat file

| File | Ano ang ginagawa | Halimbawang tanong ng panel |
|---|---|---|
| `app.py` | Sinisimulan ang web server | “Paano ito pinapatakbo?” → `python app.py` |
| `askolar/__init__.py` | Mga route (`/api/chat`, `/api/programs`, `/api/ocr/extract`), session (30 minutes), CSRF protection | “Paano ninyo pinoprotektahan ang data?” |
| `services/conversation.py` | **Facade.** Iisang pinto: dito dumadaan ang bawat mensahe at dito pinipili kung aling service ang gagamitin | “Bakit Facade?” → para hindi kailangang alamin ng UI ang bawat service |
| `services/intent.py` | Ginagamit ang **trained model** (TF-IDF + Logistic Regression) para hulaan ang intent. Kapag < 0.40 ang confidence, nagtatanong ulit | “Paano kung hindi sigurado?” |
| `services/language.py` | Hinuhulaan ang language: word list para sa malinaw na kaso, trained model para sa halo | “Paano nalalaman na Taglish?” |
| `services/smalltalk.py` | Rules para sa “hi po”, “salamat”, “bye”; sinusuri kung nagtatanong ng halaga (magkano) | “Bakit hindi intent ang greeting?” → para manatiling 7 intents at mas sigurado |
| `services/knowledge.py` | Binabasa ang `knowledge_base.json`; verified programs lang ang ipinapakita | “Saan galing ang sagot?” |
| `services/expert.py` | **Rule-Based Expert System.** Bawat rule (`>=`, `<=`, `in`) ay MET, UNMET o UNRESOLVED | “Bakit UNRESOLVED?” → kulang o hindi na-confirm ang sagot |
| `services/facts.py` | Ang 5 facts (year level, GWA, income, residency, units) at pag-check ng sagot (hal. GWA 1.00–5.00) | “Paano kung mali ang na-type?” |
| `services/ocr.py` | **Adapter.** Tesseract sa loob ng adapter; binubura agad ang upload | “Bakit Adapter?” → puwedeng palitan ang OCR tool nang hindi ginagalaw ang iba |
| `services/composer.py` | Binubuo ang sagot: answer + source + reasons + disclaimer + buttons | — |
| `services/messages.py` | Lahat ng fixed na sagot sa English at Filipino | “Paano naging bilingual?” |
| `data/knowledge_base.json` | Mga program, requirements, at rules (galing sa expert survey at interview) | “Paano magdagdag ng program?” → i-edit ang file, walang code na babaguhin |
| `training/export_from_excel.py` | Kinukuha ang tanong sa Excel → CSV | — |
| `training/train_intent.py` | Nagte-train at sumusukat ng accuracy (80/20 split) | “Ano ang parameters?” → nasa `results.md` |
| `training/train_language.py` | Nagte-train ng language identifier | — |
| `tests/test_app.py` | 45 automated tests, may Test Plan IDs (TC-xx) | “Paano ninyo nalaman na gumagana?” |
| `static/app.js`, `templates/index.html`, `static/style.css` | Ang chat UI (EN/FIL, theme, Scholarships page) | — |
