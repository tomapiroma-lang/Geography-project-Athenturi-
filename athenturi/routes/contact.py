import re

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy import update

from extensions import db
from mailer import notify
from models import Inquiry, Tour
from security import client_ip, too_many

bp = Blueprint("contact", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+()\-\s]{6,30}$")
MAX_TICKETS = 10


def validate(form, tours):
    """Return (errors, cleaned). Purchase requests need a tour and a ticket count."""
    errors = {}
    kind = form.get("kind") if form.get("kind") in ("question", "purchase") else "question"
    name, email = form.get("name", "").strip(), form.get("email", "").strip()
    phone, message = form.get("phone", "").strip(), form.get("message", "").strip()
    tour, tickets = None, None
    if not 2 <= len(name) <= 80:
        errors["name"] = "შეიყვანეთ სახელი."
    if not EMAIL_RE.match(email) or len(email) > 120:
        errors["email"] = "შეიყვანეთ სწორი ელფოსტა."
    if phone and not PHONE_RE.match(phone):
        errors["phone"] = "ტელეფონის ნომერი არასწორია."
    if kind == "purchase":
        tour = next((t for t in tours if t.slug == form.get("tour")), None)
        if tour is None:
            errors["tour"] = "აირჩიეთ ტური."
        elif tour.tickets_left <= 0:
            errors["tour"] = "ამ ტურზე ბილეთები ამოიწურა."
        try:
            tickets = int(form.get("tickets", ""))
        except ValueError:
            tickets = 0
        limit = min(MAX_TICKETS, tour.tickets_left) if tour else MAX_TICKETS
        if tour and tour.tickets_left > 0 and not 1 <= tickets <= limit:
            errors["tickets"] = f"ბილეთების რაოდენობა უნდა იყოს 1-დან {limit}-მდე."
        if len(message) > 1000:
            errors["message"] = "კომენტარი ძალიან გრძელია."
    elif not 10 <= len(message) <= 2000:
        errors["message"] = "დაწერეთ შეკითხვა (მინიმუმ 10 სიმბოლო)."
    return errors, dict(kind=kind, name=name, email=email, phone=phone, message=message, tour=tour, tickets=tickets)


@bp.route("/contact", methods=["GET", "POST"])
def index():
    tours = Tour.query.order_by(Tour.position).all()
    args = request.args
    form = dict(kind="purchase" if args.get("kind") == "purchase" else "question", tour=args.get("tour", ""),
                tickets=args.get("tickets", "1"), name=g.user.name if g.user else "",
                email=g.user.email if g.user else "", phone="", message="")
    errors = {}
    if request.method == "POST":
        form = request.form.to_dict()
        if form.get("website"):                       # honeypot: real visitors never fill this
            return redirect(url_for("contact.index"))
        if too_many(f"contact:{client_ip()}", 6, 3600):
            flash("ძალიან ბევრი შეტყობინებაა. სცადეთ მოგვიანებით.", "error")
            return render_template("contact.html", tours=tours, form=form, errors=errors), 429
        errors, d = validate(form, tours)
        if not errors and d["kind"] == "purchase":
            # Reserve tickets atomically so two buyers can't take the same seats.
            taken = db.session.execute(
                update(Tour).where(Tour.id == d["tour"].id, Tour.tickets_left >= d["tickets"])
                .values(tickets_left=Tour.tickets_left - d["tickets"])).rowcount
            if not taken:
                db.session.rollback()
                errors["tickets"] = "სამწუხაროდ, ბილეთების რაოდენობა შეიცვალა. განაახლეთ გვერდი."
        if not errors:
            total = d["tour"].price * d["tickets"] if d["kind"] == "purchase" else None
            db.session.add(Inquiry(user_id=g.user.id if g.user else None, kind=d["kind"], name=d["name"], email=d["email"],
                                   phone=d["phone"], tour_id=d["tour"].id if d["tour"] else None, tickets=d["tickets"],
                                   total=total, message=d["message"]))
            db.session.commit()
            notify(f"ათენტური: {'შეძენის მოთხოვნა' if total else 'შეკითხვა'} — {d['name']}",
                   f"{d['name']} <{d['email']}> {d['phone']}\n"
                   + (f"{d['tour'].title}, ბილეთები: {d['tickets']}, ჯამი: €{total}\n" if total else "") + f"\n{d['message']}",
                   reply_to=d["email"])
            flash("მოთხოვნა მიღებულია! ბილეთები თქვენთვის დაჯავშნილია, ჩვენ მალე დაგიკავშირდებით დასადასტურებლად."
                  if total else "მადლობა! თქვენი შეკითხვა მივიღეთ და მალე გიპასუხებთ.", "success")
            return redirect(url_for("account.index") if g.user and total else url_for("contact.index"))
    return render_template("contact.html", tours=tours, form=form, errors=errors)
