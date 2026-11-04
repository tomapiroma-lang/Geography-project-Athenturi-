from flask import Blueprint, render_template

from models import Region, Tour

bp = Blueprint("tours", __name__, url_prefix="/tours")


@bp.get("/")
def index():
    regions = Region.query.order_by(Region.position).all()
    return render_template("tours.html", regions=regions)


@bp.get("/<slug>")
def detail(slug):
    tour = Tour.query.filter_by(slug=slug).first_or_404()
    related = (Tour.query.filter(Tour.region_id == tour.region_id, Tour.id != tour.id).order_by(Tour.position).limit(3).all()
               or Tour.query.filter(Tour.id != tour.id).order_by(Tour.position).limit(3).all())
    return render_template("tour.html", t=tour, related=related)
