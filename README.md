# SwitchDeck
[![Build Status](https://travis-ci.org/dem214/switchdeck.svg?branch=master)](https://travis-ci.org/dem214/switchdeck)
[![Coverage Status](https://coveralls.io/repos/github/dem214/switchdeck/badge.svg?branch=master)](https://coveralls.io/github/dem214/switchdeck?branch=master)

## Getting Started

### Prerequisites

For work, project need [Python] of version 3.7+.

Project can work with SQLite3 and PostgreSQL databases by default.
Another databases are acceptable too with additional Python packages
(more information in
[related Django documentation](https://docs.djangoproject.com/en/2.2/ref/databases/)).

For localization compilation project needs [GNU gettext].

### Installing

* Setting local environment

 `DATABASE_URL` - full database URL path like
`postgres://USER:PASSWORD@HOST:PORT/NAME`.
 Instead, it's create SQLite3 server named `db.sqlite3` in local directory.

 `SECRET_KEY` - sequence of symbols used by Django in security issues.
 **It's highly recommended to put something there in production.**

 `DEBUG=1` - use this to run project in DEBUG mode.
 Leave untouched or another value in production mode.


* Migrating database.

 ```bash
python manage.py migrate
```

* Collecting static files.

 ```bash
python manage.py collectstatic
```

* Compile localization files (need [GNU gettext]).

 ```bash
django-admin compilemessages
```

## Built With

* [Django] - The base web framework.
* [Bootstrap] - Fancy frontend framework.
* [Crispy-forms] - Useful Bootstrap-like forms addon.
* [Django REST framework] - Help framework for building API.

## Author

[Dzmitry Izaitka](https://github.com/dem214) - Initial works.

## License

The license of the project is GNU General Public License - see [LICENSE](LICENSE) file for details.

[Bootstrap]: https://getbootstrap.com/ "https://getbootstrap.com/"
[Crispy-forms]: https://django-crispy-forms.readthedocs.io/en/latest/ "https://django-crispy-forms.readthedocs.io/en/latest/"
[Django]: https://www.djangoproject.com/ "https://www.djangoproject.com/"
[Django REST framework]: https://www.django-rest-framework.org/ "https://www.django-rest-framework.org/"
[GNU gettext]: https://www.gnu.org/software/gettext/ "https://www.gnu.org/software/gettext/"
[Python]: https://www.python.org/ "https://www.python.org/"
