from flask import Blueprint, Response, current_app, render_template

from models import Region, Tour

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    regions = Region.query.order_by(Region.position).all()
    tours = Tour.query.order_by(Tour.position).all()
    return render_template("index.html", regions=regions, tours=tours)


@bp.get("/about")
def about():
    return render_template("about.html")


@bp.get("/healthz")
def health():
    return {"status": "ok"}


@bp.get("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\nSitemap: {current_app.config['SITE_URL']}/sitemap.xml\n", mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap():
    base = current_app.config["SITE_URL"]
    paths = ["/", "/tours/", "/about", "/contact"] + [f"/tours/{t.slug}" for t in Tour.query.all()]
    body = "".join(f"<url><loc>{base}{p}</loc></url>" for p in paths)
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    + body + "</urlset>", mimetype="application/xml")
