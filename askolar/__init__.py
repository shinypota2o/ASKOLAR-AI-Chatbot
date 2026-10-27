import json
import secrets
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from .services.knowledge import KnowledgeBase
from .services.intent import IntentClassifier
from .services.conversation import ConversationManager, fresh_state
from .services.ocr import OCRAdapter

def create_app(testing=False):
    root=Path(__file__).resolve().parent.parent
    app=Flask(__name__, template_folder=str(root/'templates'), static_folder=str(root/'static'))
    app.config.update(TESTING=testing, MAX_CONTENT_LENGTH=16*1024, SESSION_TTL=1800)
    records={};lock=threading.RLock()
    manager=ConversationManager(KnowledgeBase(root/'data/knowledge_base.json'),IntentClassifier(),
                                json.loads((root/'data/demo_program.json').read_text()))
    app.extensions['temporary_sessions']=records
    def cleanup():
        now=time.monotonic()
        for key in list(records):
            if now-records[key]['seen']>app.config['SESSION_TTL']:
                del records[key]
    def janitor():
        while True:
            time.sleep(30)
            with lock: cleanup()
    if not testing:
        threading.Thread(target=janitor,daemon=True).start()
    def current():
        cleanup()
        return records.get(request.cookies.get('askolar_sid',''))
    @app.after_request
    def security(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response
    @app.errorhandler(413)
    def too_large(error):
        return jsonify(text='Request too large. Uploads are not enabled.'),413
    @app.get('/')
    def index(): return render_template('index.html')
    @app.get('/api/session')
    def session():
        with lock:
            record=current();sid=request.cookies.get('askolar_sid')
            if record is None:
                sid=secrets.token_urlsafe(32)
                record={'state':fresh_state(),'csrf':secrets.token_urlsafe(32),'seen':time.monotonic()}
                records[sid]=record
            response=jsonify(csrf=record['csrf'],intent_mode=manager.classifier.mode,
                             notice='Local development starter. No trained intent model, real policies, accounts or OCR yet.')
            response.set_cookie('askolar_sid',sid,httponly=True,samesite='Strict',secure=False)
            return response
    @app.before_request
    def protect_writes():
        if request.method=='POST':
            with lock:
                record=current()
                if not record:return jsonify(text='Session expired. Reload to start a new session.'),401
                if not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),record['csrf']):
                    return jsonify(text='Invalid request token. Reload the page.'),403
    @app.post('/api/chat')
    def chat():
        payload=request.get_json(silent=True)
        text=payload.get('message') if isinstance(payload,dict) else None
        if not isinstance(text,str) or not text.strip() or len(text)>2000:
            return jsonify(text='Enter a message of 1–2000 characters.'),400
        with lock:
            record=current()
            if not record:return jsonify(text='Session expired. Reload.'),401
            record['seen']=time.monotonic()
            return jsonify(manager.handle(record['state'],text))
    @app.post('/api/session/end')
    def end():
        with lock: records.pop(request.cookies.get('askolar_sid',''),None)
        response=jsonify(text='Temporary session facts deleted.')
        response.delete_cookie('askolar_sid')
        return response
    @app.post('/api/ocr/extract')
    def ocr(): return jsonify(OCRAdapter().extract()),501
    return app
