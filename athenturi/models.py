from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

FEW_LEFT = 5  # "few left" badge when this many tickets or fewer remain
STATUS_LABELS = {
    "available": "ბილეთები ხელმისაწვდომია",
    "few": "დარჩა ცოტა ადგილი",
    "sold": "ბილეთები ამოიწურა",
}
INQUIRY_STATUS = {"new": "ახალი", "confirmed": "დადასტურებულია", "cancelled": "გაუქმებულია"}


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    inquiries = db.relationship("Inquiry", backref="user", lazy=True)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(60), nullable=False)
    position = db.Column(db.Integer, default=0)
    tours = db.relationship("Tour", backref="region", order_by="Tour.position", lazy=True)


class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    region_id = db.Column(db.Integer, db.ForeignKey("region.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(60), nullable=False)
    duration = db.Column(db.String(60), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    tickets_total = db.Column(db.Integer, nullable=False)
    tickets_left = db.Column(db.Integer, nullable=False)
    highlights = db.Column(db.Text, default="")
    includes = db.Column(db.Text, default="")
    position = db.Column(db.Integer, default=0)

    @property
    def status(self):
        if self.tickets_left <= 0:
            return "sold"
        return "few" if self.tickets_left <= FEW_LEFT else "available"

    @property
    def status_label(self):
        return STATUS_LABELS[self.status]

    @property
    def paragraphs(self):
        return [p.strip() for p in self.description.split("\n\n") if p.strip()]

    @property
    def highlight_list(self):
        return [x.strip() for x in (self.highlights or "").splitlines() if x.strip()]

    @property
    def include_list(self):
        return [x.strip() for x in (self.includes or "").splitlines() if x.strip()]


class Inquiry(db.Model):
    """A question or a ticket purchase request sent from the contact page."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    kind = db.Column(db.String(20), nullable=False)          # question | purchase
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), default="")
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=True)
    tickets = db.Column(db.Integer, nullable=True)
    total = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="new")
    created_at = db.Column(db.DateTime, default=utcnow)
    tour = db.relationship("Tour")

    @property
    def status_label(self):
        return INQUIRY_STATUS.get(self.status, self.status)
