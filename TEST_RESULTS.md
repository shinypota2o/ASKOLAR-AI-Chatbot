# Test results (v0.3, 31 Oct 2026, development check)

- **45 automated tests passed** (`python -m unittest discover -s tests`), Python 3.13, Flask 3.1.2, scikit-learn 1.9.1.
- **Response time** (Flask test client, 20 replies): average 2.3 ms, maximum 17.9 ms (NFR-05 target: 3 s or less).
- **OCR check on 12 real PGPC class-card photos** (names covered; images not kept). Two readings: with table lines removed, then cropped and enlarged.
  | Photos | Total units (printed) | GWA (handwritten) | Fields correct | Wrong values |
  |---|---|---|---|---|
  | 8 photos on a plain background, taken straight from above | 7 of 8 | 2 of 8 | 9 of 16 (56%) | 1 (units 28 instead of 26) |
  | 4 photos on a patterned table | 2 of 4 | 0 of 4 | 2 of 8 (25%) | 0 |
  | All 12 | 9 of 12 | 2 of 12 | 11 of 24 (46%) | 1 |
  Below the M-03 target (≥ 85%). Handwritten GWA is the main problem. Every OCR value is shown to the student, who confirms or types it (FR-14, FR-15).
- **Intent model:** a trial run on the 115 unreviewed draft questions was used only to check that the scripts work. It is not a result. Train again after the group review and report only the final run.
- Not yet done: student acceptance test, Windows laptop run, offline test, real phone test.
