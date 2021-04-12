# mesolex

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

mesolex is a smart dictionary for Nahuatl (and eventually other Indigenous
languages of Mexico) built with a combination of the Django web application
framework and finite-state morphological analysis.

*NOTE: as of right now, the morphological analysis is a planned feature.
It will be added in a future phase of work.*

## Local setup for developers

mesolex is a standard Django app built for easy local development and
simple provisioning of and deployment to new instances.

Before installing, make sure you have the following prerequisites installed:

- Python 3.7
- Node 12.x
- Postgres >= 11

### Getting started

First, clone the repository and switch to the new directory:

```
$ git clone git@github.com:nmashton/mesolex.git
$ cd mesolex
```

Create a virtual environment for the project and install dependencies, for example using [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

```
$ pyenv virtualenv 3.7.1 mesolex
$ pyenv activate mesoled
(mesolex)$ pip install -r requirements/dev.txt
```

Install Node dependencies using `npm install`. It is recommended that you use [nvm](https://github.com/creationix/nvm) to keep your Node environment in sync with the project's requirements.

### Configuration settings

Configuration for this project comes from two sources: the Django settings
file (required by all Django projects) and a set of environment variables.
To make using environment variables more convenient, we use [django-dotenv](https://github.com/jpadilla/django-dotenv)
to read them in from a `.env` file in the project root.

To get things started, we just need to create a `settings/local.py` settings
file and to set up an environment variable instructing Django to use it:

```
(mesolex)$ cp mesolex/settings/local.example.py mesolex/settings/local.py
(mesolex)$ echo "DJANGO_SETTINGS_MODULE=mesolex.settings.local" > .env
```

### Database setup

mesolex uses [Postgres](https://www.postgresql.org/), a great open-source
relational database that's very well suited to building a dictionary in
that it makes JSON data very easy to work with.

To get started, create the database and run the initial migrations:

```
(mesolex)$ createdb -E UTF-8 mesolex
(mesolex)$ python manage.py migrate
```

You will now be able to load initial data via a management command, for example
(using the Nahuatl importer):

```
(mesolex)$ python manage.py import_data azz the_name_of_your_xml_file.xml
```

### Run the server

To run mesolex, just run the server as usual for a Django project:

```
(mesolex)$ python manage.py runserver
```

## Deployment

For provisioning and deployment, this project uses Ansible in combination
with the set of Tequila Ansible roles created and maintained by developers
at Caktus Group, which make deploying Django projects a snap.

For details on provisioning and deployment, see `docs/provisioning_and_deployment.md`.

## License

[Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
