# ათენტური

Georgian-language tour site for Greece-only tours. Flask + SQLAlchemy back end, plain HTML/CSS/JS front end.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # set SECRET_KEY, email, phone
python app.py                                         # http://localhost:5000
```

The database is created and filled with sample tours on first start (`instance/athenturi.db`).

## What is inside

- **Pages:** home with photo slider, tours (regional dropdowns), a page per tour, about, contact, register, login, "my requests", admin.
- **Contact form:** question or ticket purchase request. Purchases check availability, reserve the tickets in one atomic update, and show the total.
- **Admin (`/admin`):** set `ADMIN_EMAILS` in `.env`, register with that email, then confirm or cancel requests. Cancelling gives the tickets back.
- **Safety:** hashed passwords, CSRF tokens on every form, rate limits on login/register/contact, spam trap field, security headers.

## Change the content

- **Tours, regions, prices, tickets:** `seed.py`, then `flask --app app seed --reset`. This replaces regions and tours (requests are kept).
- **Photos:** `static/img/<slug>.jpg` (large) and `<slug>-sm.jpg` (card size). Keep the file name equal to the `image` value in `seed.py`.
- **Colours and fonts:** variables at the top of `static/css/style.css`.
- **Email and phone:** `.env`. Add `MAIL_*` values to also get each request by email.

## Deploy

- **Vercel:** `vercel.json` and `api/index.py` are included. Vercel's disk is temporary, so set `DATABASE_URL` to a hosted PostgreSQL database, otherwise requests and accounts disappear. Also set `SECRET_KEY`, `SITE_URL` and the other `.env` values as project variables.
- **Anywhere else:** `gunicorn app:app`

## Notes

The tour texts, prices, ticket counts and the "about" story are sample content to replace with your own.
