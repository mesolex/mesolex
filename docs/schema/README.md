# Data schemas

Dictionary data for Mesolex is stored in the `data` field of the `lexicon.Entry`
model, a JSON field containing a blob of lexical data following a language-specific format.

The formats for individual languages are documented in JSON schemas. Mesolex does not
currently use these schemas programmatically; they exist only to document the structure
of the JSON data associated with entries in the particular languages and to provide guidance
for maintainers in updating the data import scripts.

The copies of the schema checked into the project repository in this directory exist
in order to track changes to the schema. The canonical form of each schema is given
by a JSON object stored in an S3 bucket.

## TODOs

The URI of the current version of the schema should be associated with the lexical
data in some way, e.g. by annotating each piece of data with the URI or by making
the URI available in some denormalized form like a database singleton.