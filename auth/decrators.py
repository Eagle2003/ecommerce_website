from functools import wraps
from flask import session, flash, redirect, url_for, current_app

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("AUTHENTICATED") : 
            return f(*args, **kwargs) 
        else : 
            flash('Please Log in First')
            return redirect(url_for('auth.login'))
    return wrap

def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not  session.get("AUTHENTICATED") : 
            return f(*args, **kwargs)
        else : 
            flash("Page not accessible")
            return redirect(url_for('shop.landing'))
    return wrap
