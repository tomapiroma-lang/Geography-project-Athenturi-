"""ათენტური — Flask application factory."""
from flask import Flask, g, render_template, request

from config import Config
from extensions import db


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    from models import STATUS_LABELS
    from routes import account, admin, auth, contact, main, tours
    from security import check_csrf, csrf_input, csrf_token, is_admin, load_user

    for module in (main, auth, tours, contact, account, admin):
        app.register_blueprint(module.bp)

    @app.before_request
    def guard():
        if request.method == "POST":
            check_csrf()
        load_user()

    @app.context_processor
    def inject():
        c = app.config
        return dict(csrf_input=csrf_input, csrf_token=csrf_token, user=g.get("user"),
                    is_admin=is_admin(g.get("user")), site_name=c["SITE_NAME"], site_url=c["SITE_URL"],
                    site_email=c["SITE_EMAIL"], site_phone=c["SITE_PHONE"], status_labels=STATUS_LABELS)

    @app.after_request
    def headers(resp):
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; font-src https://fonts.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.path.startswith("/static/"):
            resp.headers["Cache-Control"] = "public, max-age=604800"
        return resp

    errors = {
        400: ("მოთხოვნა ვერ დადასტურდა", "განაახლეთ გვერდი და სცადეთ თავიდან."),
        404: ("გვერდი ვერ მოიძებნა", "ბმული შესაძლოა ძველია ან შეცდომითაა აკრეფილი."),
        500: ("დროებითი შეფერხება", "რაღაც არასწორად წავიდა. სცადეთ ცოტა ხანში."),
    }
    for code, (title, text) in errors.items():
        app.register_error_handler(
            code, lambda e, code=code, title=title, text=text: (render_template("error.html", code=code, title=title, text=text), code))

    from seed import register_cli, seed_if_empty
    register_cli(app)
    with app.app_context():
        db.create_all()
        seed_if_empty()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
