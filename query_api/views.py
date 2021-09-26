import json
from functools import reduce

from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from marshmallow import ValidationError

from lexicon.models import Entry
from query_api.schema import SearchSchema
from query_api.transformations.utils import apply_transformations, contains_word_to_regex, to_vln
from query_api.transformations.azz import nahuat_orthography
from query_api.transformations.spanish_thesaurus import es_thesaurus_lookup
from query_api.transformations.juxt1235 import neutralize_glottal_stop


FILTERS_DICT = {
    'begins_with': '__startswith',
    'ends_with': '__endswith',
    'contains': '__contains',
    'contains_word': '__regex',
    'exactly_equals': '',
    'regex': '__regex',
    'text_search': None,
}

TRANSFORMATIONS_DICT = {
    'azz': [contains_word_to_regex, to_vln, nahuat_orthography, es_thesaurus_lookup],
    'juxt1235_verb': [contains_word_to_regex, neutralize_glottal_stop, es_thesaurus_lookup],
    'juxt1235_non_verb': [contains_word_to_regex, neutralize_glottal_stop, es_thesaurus_lookup],
}
DEFAULT_TRANSFORMATIONS = [contains_word_to_regex]

GLOBAL_MODIFIERS_DICT = {
    'only_with_sound': Q(data__media__isnull=False),
}


def query_dict_to_q(query_dict, dataset):
    """
    Given a dict validated by query_api.schema.QuerySchema, return a Q instance
    representing a single clause of the search to be composed.
    """
    filter_type, type_tag, value, exclude = [
        query_dict[k] for k in ['filter_type', 'type_tag', 'value', 'exclude']
    ]

    modifiers = [modifier['name'] for modifier in query_dict['modifiers']]

    (filter_type, value) = apply_transformations(
        filter_type,
        value,
        modifiers,
        TRANSFORMATIONS_DICT.get(dataset, DEFAULT_TRANSFORMATIONS),
    )
    query_data = {}

    if filter_type == 'text_search':
        query_data['longsearchablestring__type_tag'] = type_tag
        query_data['longsearchablestring__searchable_value'] = SearchQuery(
            value,
            config='spanish',
        )
    else:
        query_data['searchablestring__type_tag'] = type_tag
        query_data[f'searchablestring__value{FILTERS_DICT[filter_type]}'] = value

    query = Q(**query_data)

    if exclude:
        return ~query

    return query


def queries_to_subqueryset(queries):
    """
    Given a list of Q instances, create an Entry queryset by iteratively
    filtering on the Qs (creating one big JOIN expression).
    """
    nonempty_queries = [query for query in queries if query]
    if not nonempty_queries:
        return Entry.objects.none()

    return reduce(
        lambda acc, next_Q: acc.filter(next_Q),
        nonempty_queries,
        Entry.objects,
    )


def search_query_data_to_result_queryset(dataset, search_data_query, global_modifiers):
    """
    Given a list of list of dicts validated by query_api.schema.QuerySchema,
    create a list of subqueries (each one consisting of a big JOIN expression
    created with `queries_to_subqueryset`), then combine these into one
    queryset with `.union` (creating one big SQL UNION expression).
    """
    # Create nested list of lists of Q instances
    list_of_qs = [
        [Q(dataset=dataset)] + [
            query_dict_to_q(query_dict, dataset)
            for query_dict in sub_clause
        ]
        for sub_clause in search_data_query
        if sub_clause
    ]

    global_modifiers = [
        GLOBAL_MODIFIERS_DICT[global_modifier['name']]
        for global_modifier in global_modifiers
        if global_modifier['name'] in GLOBAL_MODIFIERS_DICT
    ]

    # Transform lists of Q instances into subqueries
    list_of_subquerysets = [
        queries_to_subqueryset(queries + global_modifiers)
        for queries in list_of_qs
    ]

    # Combine subqueries with UNION
    return reduce(
        lambda acc, next_qs: acc.union(next_qs),
        list_of_subquerysets,
    )


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def search(request):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['allow'] = 'POST,OPTIONS'
        return response

    search_schema = SearchSchema()

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            status=400,
            data={'data': ['Could not decode submission.']},
        )

    try:
        search_data = search_schema.load(body)
    except ValidationError as validation_error:
        return JsonResponse(
            status=400,
            data=validation_error.messages,
        )

    result = search_query_data_to_result_queryset(
        search_data['dataset'],
        search_data['query'],
        search_data['global_modifiers'],
    )

    result = result.distinct().order_by('value')

    page = search_data['page']
    page_size = search_data['page_size']
    (start, end) = (
        (page - 1) * page_size,
        (page * page_size),
    )

    total = result.count()

    return JsonResponse({
        'page': page,
        'data': [entry.data for entry in result][start:end],
        'total': total,
        'pageSize': page_size,
    })
