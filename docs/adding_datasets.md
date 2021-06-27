# Adding new datasets

To add a new dataset to Mesolex and make it searchable, perform the following steps:

- Add definitions of the dataset's searchable data to `mesolex/config/datasets.yml`
- Add a new script to the management command definition in `lexicon/management/commands/import_data.py` to import the data
- Add a JSON schema to `docs/schema/` describing the shape of the imported data
- Add localization data to `mesolex_site/templates/mesolex_site/language_messages.js` and `mesolex_site/templates/mesolex_site/language_messages.txt`
- Add new search form definitions to `lexicon/forms/juxt1235.py` and ` lexicon/forms/__init__.py`
- Add new frontend templates in `mesolex_site/templates/mesolex_site/includes/search_result/`
- Run the import and indexaction scripts on the server(s) where you want to deploy the dataset

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
    - **NOTE:** this type tag is chosen when writing a data importer.
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