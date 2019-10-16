# SwitchDeck
[![Build Status](https://travis-ci.org/dem214/switchdeck.svg?branch=master)](https://travis-ci.org/dem214/switchdeck)
[![Coverage Status](https://coveralls.io/repos/github/dem214/switchdeck/badge.svg?branch=master)](https://coveralls.io/github/dem214/switchdeck?branch=master)

## Getting Started

### Prerequisites

For work, project need [Python](https://www.python.org/) of version 3.7+ .

### Installing

* Migrate database.

```
python manage.py migrate
```

* Collect static files.

```
python manage.py collectstatic
```

* Compile localization files.

```
django-admin compilemessages
```

## Built With

* [Django](https://www.djangoproject.com/) - The base web framework.
* [Bootstrap](https://getbootstrap.com/) - Fancy frontend framework.
* [Crispy-froms](https://django-crispy-forms.readthedocs.io/en/latest/) - Useful Bootstrap-like forms addon.
* [Django REST framework](https://www.django-rest-framework.org/) - Help framework for building API.

## Author

[Dzmitry Izaitka](https://github.com/dem214) - Initial works.

## License

The license of the project is GNU General Public License - see [LICENSE](LICENSE) file for details.
