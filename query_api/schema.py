from marshmallow import Schema, fields, validate


class ModifierSchema(Schema):
    name = fields.String(required=True)
    data = fields.Dict(missing={})


class QuerySchema(Schema):
    length = fields.String(
        missing='short',
        validate=validate.OneOf(['short', 'long']),
    )
    type_tag = fields.String(required=True)
    filter_type = fields.String(
        required=True,
        validate=validate.OneOf([
            'begins_with',
            'ends_with',
            'contains',
            'contains_word',
            'exactly_equals',
            'regex',
            'text_search',
        ]),
    )
    value = fields.String(required=True)
    exclude = fields.Boolean(missing=False)
    modifiers = fields.List(fields.Nested(ModifierSchema), missing=[])


class SearchSchema(Schema):
    page = fields.Integer(
        missing=1,
        validate=validate.Range(min=1, max=None),
    )
    page_size = fields.Integer(
        missing=25,
        validate=validate.Range(min=1, max=100),
    )
    dataset = fields.String(required=True)
    # The `query` field is a list of lists.
    # Outer list: queries to be combined by SQL union.
    # Inner list: filters to be combined by iterated SQL joins.
    query = fields.List(
        fields.List(fields.Nested(QuerySchema)),
        missing=[[]],
    )
    global_modifiers = fields.List(
        fields.Nested(ModifierSchema),
        missing=[],
    )
