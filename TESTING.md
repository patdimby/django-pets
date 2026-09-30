# Testing

Validated with Python 3.12 and Django 5.2.17. The suite currently contains **55 tests**.

```bash
python -m pip install -r requirements-dev.txt
python manage.py check --settings=backend.settings.testing
python manage.py makemigrations --check --dry-run --settings=backend.settings.testing
coverage run manage.py test --settings=backend.settings.testing
coverage report
coverage html
```

Tests use an isolated SQLite database, an in-memory email backend and fast test-only password hashing. Production databases and credentials are never required. GitHub Actions repeats the checks on pushes and pull requests.

The catalog suite checks empty installations, optional images, request-local context, demo filtering, pagination and missing products. Cart tests check quantity validation, accumulation, replacement, removal, session round trips, JSON-safe iteration, deleted products and clearing. Coupon tests cover validity periods, active status, percentage bounds, case-insensitive application and invalid form reset. Image tests cover login requirements, POST-only likes, malformed input, idempotent likes, forward/reverse count updates, URL validation and rendered pages. Activity tests check the deduplication window and target scoping.

Redis metrics are mocked; the optional cart and coupon URL modules are mounted by integration tests. No real email or remote image download occurs during the suite. Real Redis availability, image downloads, browser JavaScript and payment/order processing are outside its scope.
