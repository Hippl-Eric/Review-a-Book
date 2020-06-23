from functools import wraps
from flask import redirect, url_for, session, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def apology(message):
    return render_template('apology.html', message=message)
