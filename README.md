# juntagrico-pg


[![juntagrico-ci](https://github.com/juntagrico/juntagrico-pg/actions/workflows/juntagrico-ci.yml/badge.svg?branch=main&event=push)](https://github.com/juntagrico/juntagrico-pg/actions/workflows/juntagrico-ci.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/02bb5f131cc157fcc4b9/maintainability)](https://codeclimate.com/github/juntagrico/juntagrico-pg/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/02bb5f131cc157fcc4b9/test_coverage)](https://codeclimate.com/github/juntagrico/juntagrico-pg/test_coverage)
[![image](https://img.shields.io/pypi/v/juntagrico-pg.svg)](https://pypi.python.org/pypi/juntagrico-pg)
[![image](https://img.shields.io/pypi/l/juntagrico-pg.svg)](https://pypi.python.org/pypi/juntagrico-pg)
[![image](https://img.shields.io/pypi/pyversions/juntagrico-pg.svg)](https://pypi.python.org/pypi/juntagrico-pg)
[![image](https://img.shields.io/pypi/status/juntagrico-pg.svg)](https://pypi.python.org/pypi/juntagrico-pg)
[![image](https://img.shields.io/pypi/dm/juntagrico-pg.svg)](https://pypi.python.org/pypi/juntagrico-pg/)
[![image](https://img.shields.io/github/last-commit/juntagrico/juntagrico-pg.svg)](https://github.com/juntagrico/juntagrico-pg)
[![image](https://img.shields.io/github/commit-activity/y/juntagrico/juntagrico-pg)](https://github.com/juntagrico/juntagrico-pg)

postgres db editor for juntagrico.

This is an extension for juntagrico. You can find more information about juntagrico here
(https://github.com/juntagrico/juntagrico)

# Installation

Install juntagrico-pg via `pip`

    $ pip install juntagrico-pg

or add it in your projects `requirements.txt`

In `settings.py` add `'juntagrico_pg',` **before** juntagrico.

```python
INSTALLED_APPS = [
    ...
    'juntagrico_pg',
    'juntagrico',
]
```

In your `urls.py` you also need to extend the pattern:

```python
urlpatterns = [
    ...
    path('', include('juntagrico_pg.urls')),
]
```

# Security

The console executes any SQL with the database user of your juntagrico instance. A user with the permission
`juntagrico_pg.can_sql` can read and change all data, e.g. password hashes and session keys, and can make
themselves a superuser. Only give this permission to people you would also give superuser rights.
Superusers always have this permission.

# Settings

| Setting                 | Default | Description                                                                                       |
|-------------------------|---------|---------------------------------------------------------------------------------------------------|
| `JPG_MAX_ROWS`          | `1000`  | Maximum number of rows shown in a result.                                                         |
| `JPG_STATEMENT_TIMEOUT` | `30000` | PostgreSQL `statement_timeout` in milliseconds for queries of the console. `0` or `None` disables it. |

The row limit only limits the output. The database driver still loads the whole result into memory, so the
statement timeout is the actual protection against expensive queries.

# Logging

Every statement is logged with the executing user to the logger `juntagrico_pg` (level `INFO`, failures with
level `WARNING`). Make sure your `LOGGING` configuration keeps these messages, e.g.:

```python
LOGGING = {
    ...
    'loggers': {
        'juntagrico_pg': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

# psql meta commands

Commands starting with a backslash are executed with [pgspecial](https://github.com/dbcli/pgspecial).
Only commands that read the catalog are supported: `\d`, `\dt`, `\dv`, `\dm`, `\di`, `\ds`, `\df`, `\dn`,
`\du`, `\dx`, `\dT`, `\l` and `\h`. They accept a pattern like in psql, e.g. `\dt juntagrico_m*` or
`\d juntagrico_member`.
