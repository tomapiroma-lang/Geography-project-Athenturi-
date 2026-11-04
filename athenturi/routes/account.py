from flask import Blueprint, g, render_template

from models import Inquiry
from security import login_required

bp = Blueprint("account", __name__)


@bp.get("/account")
@login_required
def index():
    items = Inquiry.query.filter_by(user_id=g.user.id).order_by(Inquiry.created_at.desc()).all()
    return render_template("account.html", items=items)
