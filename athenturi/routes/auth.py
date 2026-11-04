import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from extensions import db
from models import User
from security import client_ip, safe_next, too_many

bp = Blueprint("auth", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _sign_in(user):
    session.clear()
    session["uid"] = user.id
    session.permanent = True


@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("tours.index"))
    form, errors = {}, {}
    if request.method == "POST":
        form = request.form
        name, email = form.get("name", "").strip(), form.get("email", "").strip().lower()
        password, again = form.get("password", ""), form.get("password2", "")
        if not 2 <= len(name) <= 80:
            errors["name"] = "შეიყვანეთ სახელი (მინიმუმ 2 სიმბოლო)."
        if not EMAIL_RE.match(email) or len(email) > 120:
            errors["email"] = "შეიყვანეთ სწორი ელფოსტა."
        elif User.query.filter_by(email=email).first():
            errors["email"] = "ამ ელფოსტით ანგარიში უკვე არსებობს."
        if len(password) < 8:
            errors["password"] = "პაროლი უნდა შეიცავდეს მინიმუმ 8 სიმბოლოს."
        elif password != again:
            errors["password2"] = "პაროლები არ ემთხვევა."
        if not errors and too_many(f"reg:{client_ip()}", 8, 3600):
            errors["email"] = "ძალიან ბევრი მცდელობაა. სცადეთ მოგვიანებით."
        if not errors:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            _sign_in(user)
            flash(f"კეთილი იყოს თქვენი მობრძანება, {name}!", "success")
            return redirect(url_for("tours.index"))
    return render_template("register.html", form=form, errors=errors)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("tours.index"))
    form = {}
    nxt = safe_next(request.values.get("next"))
    if request.method == "POST":
        form = request.form
        if too_many(f"login:{client_ip()}", 10, 600):
            flash("ძალიან ბევრი მცდელობაა. სცადეთ 10 წუთის შემდეგ.", "error")
            return render_template("login.html", form=form, next=nxt), 429
        user = User.query.filter_by(email=form.get("email", "").strip().lower()).first()
        if user and user.check_password(form.get("password", "")):
            _sign_in(user)
            flash("თქვენ წარმატებით შეხვედით ანგარიშში.", "success")
            return redirect(nxt or url_for("tours.index"))
        flash("ელფოსტა ან პაროლი არასწორია.", "error")
    return render_template("login.html", form=form, next=nxt)


@bp.post("/logout")
def logout():
    session.clear()
    flash("თქვენ გახვედით ანგარიშიდან.", "info")
    return redirect(url_for("main.index"))
