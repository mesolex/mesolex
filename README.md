# mesolex

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

mesolex is a smart dictionary for Nahuatl (and eventually other Indigenous
languages of Mexico) built with a combination of the Django web application
framework and finite-state morphological analysis.

*NOTE: as of right now, the morphological analysis is a planned feature
rather than an existing one. It will be added before the first production
release.*

## Status of project

**This doesn't work yet.** As of May 15, 2018, basic project architecture
is set up to the point where it's possible to create an environment, load data,
and do *simple* search of the text fields of lexical entries using an
interface that isn't distractingly bad. Some docs have been added,
as have a few tests. *Otherwise everything remains to be done.*
The repo has been made public to invite collaboration as early as
possible, but be warned!

Work to be done before an initial release will be tracked through one
of Github's productivity tools (*TODO:* choose one and add tickets, etc).

## Local setup for developers

mesolex is a standard Django app built for easy local development and
simple provisioning of and deployment to new instances.

Before installing, make sure you have the following prerequisites installed:

- Python >= 3.5
- pip >= 1.5
- NodeJS >= 6.11
- npm >= 2.14.7
- Postgres >= 9.5
- Java >= 8.0
- git >= 1.7

### Getting started

First, clone the repository and switch to the new directory:

```
$ git clone git@github.com:nmashton/mesolex.git
$ cd mesolex
```

Create a virtual environment for the project and install dependencies. The
following is how to do it with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/),
but you can also use pyenv or whatever other method you prefer:

```
$ mkvirtualenv mesolex -p `which python3.5`
(mesolex)$ pip install -r requirements/dev.txt
(mesolex)$ npm install
```

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

You will now be able to load initial data via a management command:

```
(mesolex)$ python manage.py load_data the_name_of_your_xml_file.xml
```

### Run the server

To run mesolex, just run the server as usual for a Django project:

```
(mesolex)$ python manage.py runserver
```

### Load some data

In order to use the project, you will need an XML file containing
a set of lexicon data. (*TODO:* make this available here or elsewhere!)
It can be loaded with a Django management command:

```
(mesolex)$ python manage.py import_data Your-Data-File.xml
```

### solr setup

The only complicated part of setting up mesolex is getting it working
with Solr, the chosen search engine backend for the project. It is
admittedly a pain, and if an easier backend can be found, the project
may soon adopt this.

To get started, install solr in your project root directory
(make sure you have Java installed!):

```
$ curl -L -O http://apache.claz.org/lucene/solr/7.3.0/solr-7.3.0.tgz
$ tar zxf solr-7.3.0.tgz
```

Create the `mesolex` search core, which is where mesolex's search
data will live:

```
solr-7.3.0/bin/solr create_core -c mesolex
```

Now comes the difficult part. Recent versions of Solr have a way of
handling the search engine schema which does not play nicely out of
the box with django-haystack, mesolex's interface with the search backend.
To get it working, you must edit `solr-7.3.0/server/solr/mesolex/conf/solrconfig.xml`.
For details, consult the project's `docs/solr_config.md`.

Once you've set up the `mesolex` configuration per those instrictions, build
the solr schema:

```
$ ./manage.py build_solr_schema > solr-7.3.0/server/solr/mesolex/conf/schema.xml
```

Then rebuild the search index using your database's contents:

```
$ ./manage.py rebuild_index
```

You should now see searches returning data as you expect.

## Deployment

For provisioning and deployment, this project uses Ansible in combination
with the set of Tequila Ansible roles created and maintained by developers
at Caktus Group, which make deploying Django projects a snap.

For details on provisioning and deployment, see `docs/provisioning_and_deployment.md`.

## License

[Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
