def reply(text, options=None, **extra):
    return dict(text=text, options=options or [], **extra)
