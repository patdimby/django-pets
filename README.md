# django-pets — Fruit Catalog & Django Modules

A Django demo combining a fruit catalog with reusable session-cart, discount-coupon and image-bookmarking modules. Its name is preserved from the original archive; the application itself focuses on fruit products and image sharing.

The project provides a practical base for studying template rendering, relational models, session persistence and small social features. Its current scope is a catalog and development demo, rather than a finished store.

## Features and status

| Component | Current behavior |
| --- | --- |
| Fruit catalog | Home, shop, product detail, about, contact, news and slider pages |
| Product management | Categories, units, product metadata and optional images; Django Admin |
| Session cart | Tested add, quantity replacement, removal, totals and JSON-safe persistence |
| Coupons | Tested percentage discounts, active/date checks and application endpoint |
| Image bookmarks | Authenticated creation/listing, likes, detail counters and popularity ranking |
| Activity log | Generic targets and a one-minute deduplication window |
| Checkout/contact/subscription | Presentation or unfinished workflow; no orders, payments or delivered emails |

The public `/cart` and `/checkout` routes remain presentation pages. The session cart and coupon URL modules are available but are not mounted in the default URL configuration. Their integration is exercised in the test suite. This distinction avoids presenting the template storefront as a complete checkout system.

## Quick start

Use Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Replace the example secret with a random value, then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> or <http://127.0.0.1:8000/admin/>. The default `manage.py` settings are `backend.settings.development`. Pages can render with an empty database; add a category, unit and product through Admin to populate the catalog. Optional location, title, breadcrumb and testimonial records enrich the templates. The distributed archive contains no preloaded database or real credentials.

## Image module

Sign in at `/accounts/login/` using a user created through Admin or `createsuperuser`. The image list is at `/images/` and the bookmarking form at `/images/create/`. There is no public registration flow.

Image detail and ranking views require a running Redis server at `localhost:6379`, database 0. Redis stores view counts and a sorted popularity ranking; SQL stores image metadata and likes. The catalog, cart and tests do not require Redis. Tests mock image metrics.

The image form downloads the supplied remote URL with a timeout and checks HTTP errors. Its extension validation is not a full upload security policy. Before opening bookmarking to untrusted users, add destination restrictions, file type and size limits, and controlled media serving. Failed network downloads still require a user-facing error workflow. Media files are served by Django only during development.

## Optional session cart integration

To expose the tested cart independently from the presentation page, add these entries to `backend/urls.py`:

```python
path('basket/', include('apps.cart.urls')),
path('coupons/', include('apps.coupons.urls')),
```

Then `/basket/` uses the session cart template and the `cart` and `coupons` URL namespaces. The storefront's existing “Add to Cart” links still lead to the presentation page; wiring them to POST forms is a separate UI integration step. No recommendation engine, order persistence or payment provider is implemented.

## Configuration

| Variable or setting | Purpose |
| --- | --- |
| `SECRET_KEY` | Required secret, unique per environment |
| `ALLOWED_HOSTS` | Comma-separated hosts; localhost by default |
| `DATABASE_URL` | Optional SQLite override locally; required in production |
| `EMAIL_BACKEND` | Console by default; tests capture mail in memory |
| `DEFAULT_FROM_EMAIL` | Defaults to webmaster@localhost |
| `CART_SESSION_ID` | `cart`, the key holding JSON session items |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` | Image metrics connection, defined in base settings |

Development enables the debug toolbar. Production disables debug mode and enables secure cookies; the toolbar app and routes are restricted to development. Legacy AnyMail provider settings remain for compatibility, but a supported provider backend and credentials must be configured before enabling delivery. Subscription POSTs explicitly return HTTP 501 until a workflow is implemented.

## Structure

```text
backend/             settings and URL configuration
apps/fructs/         catalog models, pages, forms and serializers
apps/cart/           session cart, forms and optional routes
apps/coupons/        coupon model, migration and optional routes
apps/images/         bookmarks, likes, metrics and signals
apps/actions/        generic activity log and deduplication
apps/emails/         placeholder app
templates/           catalog, image, auth and cart templates
static/              bundled presentation assets
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for component boundaries and data relationships, [TESTING.md](TESTING.md) for the 55-test suite, and [GITHUB_DESCRIPTION.md](GITHUB_DESCRIPTION.md) for repository metadata.

## Validation

```bash
python manage.py test --settings=backend.settings.testing
```

The CI workflow also checks configuration, migration consistency and coverage. The suite uses a fresh database and never sends external email or downloads remote images.

## Deployment and remaining work

Use `backend.settings.production`, provide `DATABASE_URL`, `SECRET_KEY` and `ALLOWED_HOSTS`, install your database driver, run migrations and `collectstatic`, and configure a WSGI/ASGI server, HTTPS, static/media serving and Redis. Secure-cookie settings assume HTTPS; configure your reverse proxy appropriately.

Before a commercial launch, implement order processing, stock rules, cart UI integration, payment handling and email workflows. REST serializers exist, but there is no published catalog API. The `LocalUser` model uses legacy multi-table inheritance from Django's user model, and `SubscribeModel` has an uninstalled `appname` label; neither should be mistaken for a complete account or subscription subsystem.

## License and attribution

No project license was supplied in this archive. Add the license chosen by the project owner before redistributing it as an open-source package. Preserve any notices associated with bundled third-party assets.
