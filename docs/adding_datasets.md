# Adding new datasets

To add a new dataset to Mesolex and make it searchable, perform the following steps:

- Add definitions of the dataset's searchable data to `mesolex/config/datasets.yml`
- Add a new script to the management command definition in `lexicon/management/commands/import_data.py` to import the data
- Add new search form definitions to `lexicon/forms/juxt1235.py` and ` lexicon/forms/__init__.py`
- Add new frontend templates in `mesolex_site/templates/mesolex_site/includes/search_result/`
- Run the import and indexation scripts on the server(s) where you want to deploy the dataset

The above steps are *necessary*; "nice-to-have" steps that make the dataset fully user- and developer-friendly also include:

- Add a JSON schema to `docs/schema/` describing the shape of the imported data
- Add localization data to `mesolex_site/templates/mesolex_site/language_messages.js` and `mesolex_site/templates/mesolex_site/language_messages.txt`

These steps are broken down below, with reference to events in the Git history that provide a good
illustration of the process.

## Add searchable data definitions

Data imported into Mesolex is saved in the form of JSON documents attached to the `data` field of the `lexicon.models.Entry` model.
Because of our need to accommodate a wide variety of datasets, these JSON documents are not required to follow any
particular schema. In order to make this freeform data searchable, Mesolex uses a specification of the searchable features
of datasets' imported documents, given in the YAML document `mesolex/config/datasets.yml`.

**NOTE:** there is a good deal of "legacy" structure to the dataset specification in need of cleanup.
These remnants of old implementations will be noted and apologized for as we go.

When adding a new dataset, start by adding the following scaffolding structure:

```yaml
your_language_identifier:
  label: A human-readable label for the dataset
  code: glottocode_or_whatever_for_the_language
  extra_fields: []
  filterable_fields: []
  global_filters: []
  search_fields: []
  controlled_vocab_fields: []
```

Each of those list fields represents a different feature of the imported dataset's search capabilities.

**tl;dr:** the only required data is the `label`, `code`, and `filterable_fields` for your dataset.
Add these and the dataset will be ready to support precise string queries.

### Filterable fields

`filterable_fields` defines the basic queryable aspects of the dataset. Without specifying it, users won't
be able to do much with the dataset!

A basic filterable field definition looks like this:

```yaml
filterable_fields:
  - field: lemma
    label: Entrada
    tag: lemma
    length: short
```

The meaning of the different components:

- `field`: the internal identifier of the field, used when making specific references to the field within
  the app logic. For example, if a field has some special behavior in the frontend, that behavior
  may be triggered by seeing the string in `field`.
- `label`: the human-readable label of the field presented to the user in the UI.
- `tag`: the "type tag" associated with this field when it's indexed via a `lexicon.models.SearchableString`
  or `lexicon.models.LongSearchableString` model instance.
    - **NOTE:** this type tag is [chosen when writing a data importer](#type_tag_importer). <a name="type_tag_dataset"></a>
- `length`: one of either `short` or `long`, specifying whether this field gets indexed by `SearchableString`
  or `LongSearchableString`.
    - [Used within QueryBuilderForm](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/forms.py#L205)
    to handle search query construction.
    - **NOTE:** this is redundant given the existence of `search_fields`, and one
    or the other could be eliminated!

A filterable field with these values is sufficiently specified. There is also one optional
field, `user_languages`:

```yaml
- field: word_class_en
  label: Cat. gram.
  tag: word_class_en
  length: short
  user_languages:
    - en
```

This is used within the UI to determine when to present the field to the user.
If their session language configuration specifies that they are using the Spanish
version of the site, for example, they will not see entries with `user_languages: [en]`.
[See UI's specification of the filterable fields to display.](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/static/ts/components/query-builder-formset.tsx#L112)

### Search fields

Search fields are almost identical to filterable fields, except they are identified as
extended prose that will be searched using Postgres's full text search capabilities.
Their structure is almost identical to filterable fields, and the semantics are
the same.

```yaml
search_fields:
  - field: precise_meaning
    label: Significado preciso
    tag: sense
    length: long
```

[See how the placement into one or another category changes query construction.](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/forms.py#L200)

### Controlled vocabulary fields

For some fields given in `filterable_fields`, there's a small set of possible values that
are known in advance and have special names, e.g. grammatical categories. The user should
be able to pick from this list in the UI rather than searching the values as freeform
text. The `controlled_vocab_fields` list specifies which items in `filterable_fields`
to treat this way.

A controlled vocab field definition consists of a `field` (with the usual meaning)
and a list of `items`, each of which contains a `value` used by the backend in
querying the database and a human-readable `label`:

```yaml
controlled_vocab_fields:
  - field: part_of_speech
    items:
      - value: Adj
        label: Adjetivo
      - value: Adv
        label: Adverbio
  - field: inflectional_type
    items:
      - value: Clase 1
        label: Verbo clase 1 (kwa)
      - value: Clase 2a
        label: Verbo clase 2a (pale:wia)
```

This distinction is basically used only by the UI, which [chooses the type of form input](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/static/ts/components/query-builder-form.tsx#L293) based on whether or not the item is in the controlled vocab fields.


### Extra fields

<a name="extra_fields"></a>

The `extra_fields` data is used to specify yes/no options that can be added to search
sub-component of a search query. For example, if your dataset supports glottal stop
neutralization, this is where you declare that.

```yaml
extra_fields:
  - field: neutralize_glottal_stop
    label: Neutralizar la oclusión glotal
    constraints:
      - no_regex
```

`field` and `label` have the same semantics as in filterable and searchable fields.

`constraints` specifies a list of identifiers that can be used by the frontend
or backend to constrain the behavior of the search interface. For example, the
constraint `no_regex` prevents the filter type "regular expression" from being
usable if the field in question is selected. [See the UI for the use of constraints.](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/static/ts/components/query-builder-form.tsx#L116)

Right now, `no_regex` is the only supported constraint.


### Global filters

Datasets can support yes/no options that apply to an entire search query
rather than particular field sub-queries. For example, you may want to allow
a search to return only entries with associated audio.

Global filters contain only a field name and a label:

```yaml
global_filters:
  - field: only_with_sound
    label: Sólo mostrar entradas con sonidos
```

Global filters are [intersected with subqueries](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/forms.py#L332).
They are presented in the UI [beneath subquery forms](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/static/ts/components/query-builder-formset.tsx#L167).


## Add an import script

Actually importing data into the database has so far been done via Python scripts
written as [custom Django management commands](https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/),
which are run by invoking `python manage.py import_data`. The main advantage of using
management commands is that you can use the Django ORM to work with the database.

**NOTE:** nothing forces you to import data using these management commands. Data
could in principle be imported with raw SQL scripts. But we haven't done this yet
(as of June 27, 2021).

Import scripts live in [lexicon/management/commands/import_data.py](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/management/commands/import_data.py).
This module defines a bunch of helper classes for parsing XML and CSV documents,
but you don't have to use those if you don't like them.

### The basic importer API

`import_data` assumes that you've defined some importer logic that is called
by calling a callable thing on a string identifying the dataset and the string
path of the dataset source file & then calling the return value of that.
That second callable is expected to return a 3-tuple `(added_entries, updated_entries, total)`.

```python
importer = self._importer_for(dataset, input_file)

(added_entries, updated_entries, total) = (
    importer()
    if importer is not None
    else (0, 0, 0)
)
```

Whatever your `importer` there does is good enough, provided it meets the following guidelines!

### The basic import steps

The anatomy of a data import is spelled out pretty well by the contents of [the `process_row` method](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/management/commands/import_data.py#L778) of `Juxt1235VerbImporter`. We'll break these steps down further below.

The steps followed in the existing import scripts look roughly like the following.

- `initialize_data(row)`
  - For each item in the dataset source (XML node, CSV row), either create an `Entry`
    instance in the DB or find one by its uniquely identifying data if it already exists.
    Hold onto it for the rest of the process.
    - The `models.Entry.objects.get_or_create` function is used to [find or create
    the entry entity.](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/management/commands/import_data.py#L728)
    - Entries are uniquely identifiable by their `identifier` and `dataset` values.
  - Initialize the entry with some basic data.
    - Set the entry instance's `value` to the headword for the entry.
  - Create a dictionary that'll hold the JSON document for the entry as you construct
    it. [Hold onto that dictionary](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/management/commands/import_data.py#L735).
- `clean_up_associated_data(entry)`
  - **Erase existing `SearchableString` and `LongSearchableString` data
    associated with the entry.** These are just search indexes; they don't need
    to persist between updates and can just be tossed and re-created on each import.
- `create_simple_string_data(row, entry, entry_data)`
  - For each item in the dataset source, create a `(Long)SearchableString` to index
  the searchable feature of the data and add some data to the entry's data dictionary.
  - A searchable string instance contains the following ([see here](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/management/commands/import_data.py#L753)):
    - `value`: the searchable string itself
    - `entry`: a reference to the entry instance you created
    - `dataset`: the code of the dataset (e.g. `juxt1235`)
    - `type_tag`: the tag used to query this search field; [see how this is used in the dataset definition](#type_tag_dataset) <a name="type_tag_importer"></a>
  - If you want, you can put the searchable string model instances into a list and [bulk-create them](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/management/commands/import_data.py#L775).
- `entry.data = entry_data`
  - Add the data dictionary you've constructed to the entry's `data` property.
- `entry.save()`
  - Save the entry.

### Document your implicit schema

You have total freedom to define the shape of your imported data documents however you think
will be convenient for query or display. Go nuts!

However, it would be nice if you documented your decisions for future maintainers (including
yourself two weeks from now). We have been documenting the JSON document shapes with
[JSON schema](https://json-schema.org/) definitions in `docs/schema/`. Right now, these
docs are just documentation and are not used by the code in any way.


## Search form definitions

To actually search the data, the Django application needs to know how to use it. This
is defined by instantiating some Form(Set) classes with some references to the dataset
configuration and making them available to the search code.

Once you've added a dataset, add a new module inside `lexicon/forms/`, e.g. [`lexicon/forms/azz.py`](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/azz.py).
Fill it in adding dataset-specific subclasses of [`QueryBuilderBaseFormset`](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/forms.py#L268)
and [`QueryBuilderForm`](https://github.com/mesolex/mesolex/blob/dataset-docs/query_builder/forms.py#L77).
Access your dataset definition by [instantiating `Dataset` on the code
for your dataset](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/azz.py#L9), which
will give you access to [`filterable_fields` etc](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/azz.py#L13)
in a way the query builder classes understand.

**NOTE:** [`controlled_vocab_fields`](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/azz.py#L35) hasn't
been abstracted out yet, which is annoying.

If your dataset supports any "transformations" [triggered by `extra_fields`](#extra_fields), add the functions
that implement those transformations in [the `transformations` property](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/juxt1235_non_verb.py#L20).

Make your new formset available [in the index module in that directory](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/__init__.py),
specifically within the [`formset_for_dataset` function](https://github.com/mesolex/mesolex/blob/dataset-docs/lexicon/forms/__init__.py#L9).


## Frontend templates

To make it possible to display search result data specific to your dataset, you must add some new
templates for rendering results.

Add a new template fragment to represent an individual search result to `mesolex_site/templates/mesolex_site/includes/search_result/`.
It should look [something like this](https://github.com/mesolex/mesolex/blob/dataset-docs/mesolex_site/templates/mesolex_site/includes/search_result/juxt1235_non_verb.html).

Next, add a clause to [mesolex_site/templates/mesolex_site/search_page.html](https://github.com/mesolex/mesolex/blob/dataset-docs/mesolex_site/templates/mesolex_site/search_page.html)
telling the frontend to [use that template fragment for a search result if it matches the right dataset code](https://github.com/mesolex/mesolex/blob/dataset-docs/mesolex_site/templates/mesolex_site/search_page.html#L28).


## Run the scripts

You are now ready to actually import data. Assuming you want to import it on a deployment, upload
the source file onto the server somehow, `ssh` into that environment,
and do something like the following:

```
$ sudo su - mesolex
$ cd /var/www/mesolex
$ ./manage.sh import_data juxt1235_non_verb /home/nmashton/SMD-Base_de_datos_lexica-2021-02-13.csv
```

If your dataset includes any "long" strings that you want to make searchable via
full text search, also run (from that same directory, also as `mesolex`):

```
$ ./manage.sh update_search_vectors
```


## Localization

The Mesolex interface uses [Django's internationalization and localization](https://docs.djangoproject.com/en/3.2/topics/i18n/)
features to provide Spanish and English translations of its strings.

By default, Django's translation string generation only picks up on strings used within
basic Django source files (Python modules, HTML templates) and JavaScript / TypeScript files.
This means that strings used within `datasets.yml` aren't detected by default. To work around
this, we add strings manually to locations where Django can see them:

- `mesolex_site/templates/mesolex_site/dataset_messages.txt` for Python translations
- `mesolex_site/templates/mesolex_site/dataset_messages.js` for JavaScript translations

For all "Label" values you've added to `datasets.yml` that you want to make translatable, add
new entries to those files. Then in your local environment, run:

```
$ python manage.py makemessages --domain=django
$ python manage.py makemessages --domain=djangojs --extension=js,jsx,tsx --ignore=node_modules
```

This should result in some changes to the `.po` translation string files in `mesolex/locale/en` and
`mesolex/locale/en-us`. Find the additions to those files and fill in the English translations
of your strings. **Be sure to commit those changes.**

To see the changes locally, run:

```sh
$ python manage.py compilemessages
```

Note that this will take place automatically during deploys.