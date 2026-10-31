"""Train and evaluate ASKOLAR's intent classifier (TF-IDF + Logistic Regression).

Steps (matches SRS 5.3 and Coding Standards 3.1):
1. Load the group-made dataset (training/intent_dataset.csv).
2. Split 80/20 with a fixed seed, keeping each paraphrase group in ONE split.
3. Fit TF-IDF + Logistic Regression on the 80% training split only.
4. Report accuracy, precision, recall, F1, confusion matrix and per-language accuracy
   on the 20% test split -> training/results.md and training/results.json.
5. Refit on all questions and save the model to models/intent_model.joblib.

Usage:
    python training/train_intent.py
    python training/train_intent.py --reviewed-only
    python training/train_intent.py --reviewed-only --test-contributor "Student survey"

Review status (Intent Review Guide): Approved and Edited rows are reviewed; rows marked
Remove / Removed are never used. --test-contributor tests on real student questions (rows whose
Contributor starts with that text) and trains on all other rows.
"""
import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parent.parent
LABELS = ['availability', 'requirements', 'eligibility', 'deadline',
          'application_procedure', 'general_info', 'out_of_scope']
REVIEWED = {'approved', 'edited', 'reviewed'}
REMOVED = {'remove', 'removed'}  # the Excel dropdown uses "Removed"
SETTINGS = {
    'word_ngram_range': (1, 2),
    'char_ngram_range': (2, 4),
    'C': 5.0,
    'max_iter': 2000,
    'class_weight': 'balanced',
    'test_share': 0.2,
    'random_state': 42,
    'confidence_threshold': 0.40,
}


def load(path, reviewed_only):
    with open(path, encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r.get('text') and r.get('label')]
    bad = sorted({r['label'] for r in rows} - set(LABELS))
    if bad:
        raise SystemExit(f'Unknown intent labels in dataset: {bad}. Use only: {LABELS}')
    rows = [r for r in rows if r.get('review_status', '').strip().lower() not in REMOVED]
    if reviewed_only:
        rows = [r for r in rows if r.get('review_status', '').strip().lower() in REVIEWED]
    for r in rows:
        r['group'] = r.get('paraphrase_group') or r.get('question_id') or r['text']
    return rows


def build_pipeline():
    features = FeatureUnion([
        ('word', TfidfVectorizer(lowercase=True, analyzer='word', ngram_range=SETTINGS['word_ngram_range'], sublinear_tf=True)),
        ('char', TfidfVectorizer(lowercase=True, analyzer='char_wb', ngram_range=SETTINGS['char_ngram_range'], sublinear_tf=True)),
    ])
    model = LogisticRegression(C=SETTINGS['C'], max_iter=SETTINGS['max_iter'], class_weight=SETTINGS['class_weight'])
    return Pipeline([('tfidf', features), ('clf', model)])


def split(rows):
    folds = round(1 / SETTINGS['test_share'])
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=SETTINGS['random_state'])
    labels = [r['label'] for r in rows]
    groups = [r['group'] for r in rows]
    train_idx, test_idx = next(splitter.split(rows, labels, groups))
    return [rows[i] for i in train_idx], [rows[i] for i in test_idx]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data', default=str(ROOT / 'training' / 'intent_dataset.csv'))
    parser.add_argument('--out', default=str(ROOT / 'models' / 'intent_model.joblib'))
    parser.add_argument('--reviewed-only', action='store_true', help='use only rows marked Approved or Edited')
    parser.add_argument('--test-contributor', help='test on rows whose Contributor starts with this text, e.g. "Student survey"')
    args = parser.parse_args()

    rows = load(args.data, args.reviewed_only)
    if len(rows) < 30:
        raise SystemExit(f'Only {len(rows)} questions found; add more before training.')
    if args.test_contributor:
        prefix = args.test_contributor.lower()
        test = [r for r in rows if r.get('contributor', '').lower().startswith(prefix)]
        train = [r for r in rows if r not in test]
        if not test:
            raise SystemExit(f'No rows with Contributor starting with "{args.test_contributor}".')
    else:
        train, test = split(rows)

    pipeline = build_pipeline()
    pipeline.fit([r['text'] for r in train], [r['label'] for r in train])
    predicted = pipeline.predict([r['text'] for r in test])
    actual = [r['label'] for r in test]

    accuracy = accuracy_score(actual, predicted)
    report = classification_report(actual, predicted, labels=LABELS, zero_division=0, output_dict=True)
    report_text = classification_report(actual, predicted, labels=LABELS, zero_division=0)
    matrix = confusion_matrix(actual, predicted, labels=LABELS).tolist()
    by_language = {}
    for lang in sorted({r.get('language', '') for r in test}):
        idx = [i for i, r in enumerate(test) if r.get('language', '') == lang]
        by_language[lang or 'unknown'] = {'n': len(idx), 'accuracy': round(accuracy_score([actual[i] for i in idx], [predicted[i] for i in idx]), 4)}

    results = {
        'date': date.today().isoformat(),
        'sklearn_version': sklearn.__version__,
        'dataset': Path(args.data).name,
        'reviewed_only': args.reviewed_only,
        'test_split': f'contributor starts with "{args.test_contributor}"' if args.test_contributor else '20% paraphrase-group split',
        'total_questions': len(rows),
        'per_intent': dict(Counter(r['label'] for r in rows)),
        'per_language': dict(Counter(r.get('language', '') for r in rows)),
        'review_status': dict(Counter(r.get('review_status', '') for r in rows)),
        'train_size': len(train),
        'test_size': len(test),
        'settings': {k: list(v) if isinstance(v, tuple) else v for k, v in SETTINGS.items()},
        'accuracy': round(accuracy, 4),
        'macro_precision': round(report['macro avg']['precision'], 4),
        'macro_recall': round(report['macro avg']['recall'], 4),
        'macro_f1': round(report['macro avg']['f1-score'], 4),
        'per_label': {k: {m: round(v[m], 4) for m in ('precision', 'recall', 'f1-score', 'support')} for k, v in report.items() if k in LABELS},
        'accuracy_by_language': by_language,
        'confusion_matrix': {'labels': LABELS, 'rows_actual_cols_predicted': matrix},
    }
    out_dir = ROOT / 'training'
    (out_dir / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    md = [
        '# Intent Model Training Results', '',
        f'Date: {results["date"]} | scikit-learn {results["sklearn_version"]} | dataset: {results["dataset"]}'
        + (' (reviewed only)' if args.reviewed_only else ''), '',
        f'Questions: {len(rows)} | Train: {len(train)} | Test: {len(test)} | Test split: {results["test_split"]} (seed {SETTINGS["random_state"]})', '',
        f'**Accuracy: {accuracy:.2%}** | Macro precision {results["macro_precision"]:.2f} | Macro recall {results["macro_recall"]:.2f} | Macro F1 {results["macro_f1"]:.2f}', '',
        '```', report_text, '```', '',
        'Accuracy by language: ' + ', '.join(f'{k} {v["accuracy"]:.0%} (n={v["n"]})' for k, v in by_language.items()), '',
        'Confusion matrix (rows = actual, columns = predicted): ' + ', '.join(LABELS), '',
        '```', *[f'{LABELS[i]:<22} {row}' for i, row in enumerate(matrix)], '```', '',
        'Settings: ' + json.dumps(results['settings']),
    ]
    (out_dir / 'results.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    # Final model: refit on every question so the chatbot learns from all of them.
    final = build_pipeline()
    final.fit([r['text'] for r in rows], [r['label'] for r in rows])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'pipeline': final, 'labels': LABELS, 'threshold': SETTINGS['confidence_threshold'],
                 'test_accuracy': results['accuracy'], 'trained_on': len(rows), 'created': results['date'],
                 'sklearn_version': sklearn.__version__}, args.out)

    print('\n'.join(md))
    print(f'\nSaved model to {args.out}')


if __name__ == '__main__':
    main()
