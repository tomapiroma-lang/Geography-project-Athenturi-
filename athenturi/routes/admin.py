from flask import Blueprint, abort, flash, redirect, render_template, url_for

from extensions import db
from models import Inquiry
from security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/")
@admin_required
def index():
    items = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(200).all()
    return render_template("admin.html", items=items)


@bp.post("/inquiry/<int:inquiry_id>/<action>")
@admin_required
def update(inquiry_id, action):
    inq = db.get_or_404(Inquiry, inquiry_id)
    if action not in ("confirm", "cancel"):
        abort(404)
    if action == "confirm" and inq.status == "new":
        inq.status = "confirmed"
    elif action == "cancel" and inq.status != "cancelled":
        if inq.kind == "purchase" and inq.tour and inq.tickets:      # give the seats back
            inq.tour.tickets_left = min(inq.tour.tickets_total, inq.tour.tickets_left + inq.tickets)
        inq.status = "cancelled"
    db.session.commit()
    flash("სტატუსი განახლდა.", "success")
    return redirect(url_for("admin.index"))
