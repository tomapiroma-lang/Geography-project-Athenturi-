"""CSRF, login helpers and a tiny in-memory rate limiter."""
import secrets
import time
from collections import defaultdict, deque
from functools import wraps

from flask import abort, current_app, flash, g, redirect, request, session, url_for
from markupsafe import Markup

from extensions import db

_hits = defaultdict(deque)


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


def csrf_input():
    return Markup(f'<input type="hidden" name="_csrf" value="{csrf_token()}">')


def check_csrf():
    sent = request.form.get("_csrf", "")
    if not sent or not secrets.compare_digest(sent, session.get("_csrf", "")):
        abort(400)


def load_user():
    from models import User
    uid = session.get("uid")
    g.user = db.session.get(User, uid) if uid else None


def is_admin(user):
    return bool(user) and user.email in current_app.config["ADMIN_EMAILS"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("ამ გვერდის სანახავად გთხოვთ, შეხვიდეთ ანგარიშში.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_admin(g.user):
            abort(404)
        return view(*args, **kwargs)
    return wrapped


def safe_next(target):
    """Only allow local redirects."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return None


def client_ip():
    return (request.headers.get("x-forwarded-for", request.remote_addr or "").split(",")[0]).strip()


def too_many(key, limit, window):
    now, q = time.time(), _hits[key]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    return False
