"""Train ASKOLAR's language identifier (English / Filipino / Taglish).

It reuses the Language column of our intent dataset, so no new data is needed.
Model: TF-IDF character n-grams + Logistic Regression (scikit-learn), 80/20 split
with a fixed seed, paraphrase groups kept in one split.
Results -> training/language_results.md; model -> models/language_model.joblib.

Usage:
    python training/train_language.py
"""
import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path

import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = ['English', 'Filipino', 'Taglish']
SEED = 42


def build_pipeline():
    return Pipeline([
        ('tfidf', TfidfVectorizer(lowercase=True, analyzer='char_wb', ngram_range=(2, 4), sublinear_tf=True)),
        ('clf', LogisticRegression(C=5.0, max_iter=2000, class_weight='balanced')),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data', default=str(ROOT / 'training' / 'intent_dataset.csv'))
    parser.add_argument('--out', default=str(ROOT / 'models' / 'language_model.joblib'))
    args = parser.parse_args()

    with open(args.data, encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r.get('text') and r.get('language') in LANGUAGES
                and r.get('review_status', '').strip().lower() not in ('remove', 'removed')]
    if len(rows) < 30:
        raise SystemExit(f'Only {len(rows)} labeled questions found; add more before training.')
    groups = [r.get('paraphrase_group') or r['text'] for r in rows]
    labels = [r['language'] for r in rows]
    train_idx, test_idx = next(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED).split(rows, labels, groups))
    train, test = [rows[i] for i in train_idx], [rows[i] for i in test_idx]

    model = build_pipeline().fit([r['text'] for r in train], [r['language'] for r in train])
    predicted = model.predict([r['text'] for r in test])
    actual = [r['language'] for r in test]
    accuracy = accuracy_score(actual, predicted)
    report = classification_report(actual, predicted, labels=LANGUAGES, zero_division=0)
    md = ['# Language Identifier Results', '',
          f'Date: {date.today().isoformat()} | scikit-learn {sklearn.__version__} | questions: {len(rows)} '
          f'({dict(Counter(labels))}) | train {len(train)} | test {len(test)} | seed {SEED}', '',
          f'**Accuracy: {accuracy:.2%}**', '', '```', report, '```']
    (ROOT / 'training' / 'language_results.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    final = build_pipeline().fit([r['text'] for r in rows], labels)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'pipeline': final, 'labels': LANGUAGES, 'trained_on': len(rows), 'test_accuracy': round(accuracy, 4),
                 'created': date.today().isoformat(), 'sklearn_version': sklearn.__version__}, args.out)
    print('\n'.join(md))
    print(f'\nSaved model to {args.out}')


if __name__ == '__main__':
    main()
