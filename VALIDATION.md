# Validation report

Executed locally on Python 3.12.14 with the pinned requirements. GitHub Actions has been configured but has not been run on GitHub.

## `python manage.py check --settings=backend.settings.testing`

```text
System check identified no issues (0 silenced).
```

## `python manage.py makemigrations --check --dry-run --settings=backend.settings.testing`

```text
No changes detected
```

## `python -m coverage run manage.py test --settings=backend.settings.testing`

```text
Creating test database for alias 'default'...
.......................................................
----------------------------------------------------------------------
Ran 55 tests in 0.455s

OK
Destroying test database for alias 'default'...
Found 55 test(s).
System check identified no issues (0 silenced).
```

## `python -m coverage report`

```text
Name                              Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------
apps/__init__.py                      0      0      0      0   100%
apps/actions/__init__.py              0      0      0      0   100%
apps/actions/models.py               13      0      0      0   100%
apps/actions/utils.py                16      0      4      0   100%
apps/actions/views.py                 1      1      0      0     0%   1
apps/cart/__init__.py                 0      0      0      0   100%
apps/cart/cart.py                    70      0     20      0   100%
apps/cart/context_processors.py       3      3      0      0     0%   1-5
apps/cart/forms.py                    6      0      0      0   100%
apps/cart/models.py                   1      0      0      0   100%
apps/cart/urls.py                     4      0      0      0   100%
apps/cart/views.py                   28      0      4      0   100%
apps/coupons/__init__.py              0      0      0      0   100%
apps/coupons/forms.py                 4      0      0      0   100%
apps/coupons/models.py               10      1      0      0    90%   18
apps/coupons/urls.py                  4      0      0      0   100%
apps/coupons/views.py                18      0      2      0   100%
apps/emails/__init__.py               0      0      0      0   100%
apps/emails/models.py                 1      0      0      0   100%
apps/emails/views.py                  1      1      0      0     0%   1
apps/fructs/__init__.py               0      0      0      0   100%
apps/fructs/forms.py                 17     17      0      0     0%   1-22
apps/fructs/models.py                93      8      0      0    91%   14, 25, 32, 46, 82, 91, 99, 120
apps/fructs/serializers.py           10     10      0      0     0%   1-12
apps/fructs/urls.py                   3      0      0      0   100%
apps/fructs/views.py                 44      1      0      0    98%   81
apps/images/__init__.py               0      0      0      0   100%
apps/images/forms.py                 30      1      4      1    94%   41
apps/images/models.py                25      1      2      1    93%   31, 34->36
apps/images/signals.py               16      0      8      0   100%
apps/images/urls.py                   4      0      0      0   100%
apps/images/views.py                 73     14     12      2    76%   27-38, 91-97, 99
-----------------------------------------------------------------------------
TOTAL                               495     58     56      4    88%
```
