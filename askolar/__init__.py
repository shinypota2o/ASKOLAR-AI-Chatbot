"""Flask app: routes, CSRF protection and isolated temporary sessions."""
import json
import secrets
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .services.conversation import ConversationManager, fresh_state
from .services.intent import IntentClassifier
from .services.knowledge import KnowledgeBase
from .services.language import LanguageIdentifier
from .services.ocr import MAX_UPLOAD_BYTES, OCRAdapter, OCRError

SESSION_TTL_SECONDS = 1800  # 30 minutes of inactivity (SRS NFR-07)


def create_app(testing=False, classifier=None, knowledge_path=None, ocr_adapter=None, language=None):
    root = Path(__file__).resolve().parent.parent
    app = Flask(__name__, template_folder=str(root / 'templates'), static_folder=str(root / 'static'))
    app.config.update(TESTING=testing, MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES + 64 * 1024, SESSION_TTL=SESSION_TTL_SECONDS)

    records = {}
    lock = threading.RLock()
    demo = json.loads((root / 'data' / 'demo_program.json').read_text(encoding='utf-8'))
    knowledge = KnowledgeBase(knowledge_path or root / 'data' / 'knowledge_base.json', demo=demo)
    classifier = classifier or IntentClassifier(root / 'models' / 'intent_model.joblib')
    language = language or LanguageIdentifier(root / 'models' / 'language_model.joblib')
    manager = ConversationManager(knowledge, classifier, language)
    ocr_adapter = ocr_adapter or OCRAdapter()
    app.extensions['temporary_sessions'] = records
    app.extensions['askolar_manager'] = manager

    def cleanup():
        now = time.monotonic()
        for key in list(records):
            if now - records[key]['seen'] > app.config['SESSION_TTL']:
                del records[key]

    def janitor():
        while True:
            time.sleep(30)
            with lock:
                cleanup()

    if not testing:
        threading.Thread(target=janitor, daemon=True).start()

    def current():
        cleanup()
        return records.get(request.cookies.get('askolar_sid', ''))

    @app.after_request
    def security(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        return response

    @app.errorhandler(413)
    def too_large(error):
        return jsonify(text='The file is too large. Please upload an image smaller than 5 MB, or type your answers.'), 413

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/session')
    def session():
        with lock:
            record = current()
            sid = request.cookies.get('askolar_sid')
            if record is None:
                sid = secrets.token_urlsafe(32)
                record = {'state': fresh_state(), 'csrf': secrets.token_urlsafe(32), 'seen': time.monotonic()}
                records[sid] = record
            response = jsonify(csrf=record['csrf'], intent_mode=manager.classifier.mode, language_mode=language.mode)
            response.set_cookie('askolar_sid', sid, httponly=True, samesite='Strict', secure=False)
            return response

    @app.before_request
    def protect_writes():
        if request.method == 'POST':
            with lock:
                record = current()
                if not record:
                    return jsonify(text='Session expired. Reload to start a new session.'), 401
                if not secrets.compare_digest(request.headers.get('X-CSRF-Token', ''), record['csrf']):
                    return jsonify(text='Invalid request token. Reload the page.'), 403

    @app.post('/api/chat')
    def chat():
        payload = request.get_json(silent=True)
        text = payload.get('message') if isinstance(payload, dict) else None
        preference = payload.get('lang') if isinstance(payload, dict) else None
        if not isinstance(text, str) or not text.strip() or len(text) > 2000:
            return jsonify(text='Enter a message of 1–2000 characters.'), 400
        with lock:
            record = current()
            if not record:
                return jsonify(text='Session expired. Reload.'), 401
            record['seen'] = time.monotonic()
            answer = manager.handle(record['state'], text, preference if preference in ('en', 'fil') else 'auto')
            answer['lang'] = record['state']['lang']
            return jsonify(answer)

    @app.get('/api/programs')
    def programs():
        """Scholarships page: verified programs only, no personal data."""
        return jsonify(knowledge.public_list())

    @app.post('/api/session/end')
    def end():
        with lock:
            records.pop(request.cookies.get('askolar_sid', ''), None)
        response = jsonify(text='Temporary session facts deleted.')
        response.delete_cookie('askolar_sid')
        return response

    @app.post('/api/ocr/extract')
    def ocr():
        upload = request.files.get('file')
        with lock:
            record = current()
            if not record:
                return jsonify(text='Session expired. Reload.'), 401
            record['seen'] = time.monotonic()
            if not manager.ocr_allowed(record['state']):
                return jsonify(text='You can upload a grade report only while answering eligibility questions, '
                                    'after agreeing to the privacy notice.'), 409
        if upload is None:
            return jsonify(text='No file was received.'), 400
        try:
            extracted = ocr_adapter.extract(upload.read(), upload.mimetype)
        except OCRError as error:
            with lock:
                return jsonify(manager.ocr_failed(record['state'], str(error))), 422
        with lock:
            return jsonify(manager.handle_ocr(record['state'], extracted['fields']))

    return app
