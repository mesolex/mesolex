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


FILTERS_DICT = {
    'begins_with': '__startswith',
    'ends_with': '__endswith',
    'contains': '__contains',
    'contains_word': '__regex',
    'exactly_equals': '',
    'regex': '__regex',
    'text_search': None,
}


def query_dict_to_q(query_dict):
    """
    Given a dict validated by query_api.schema.QuerySchema, return a Q instance
    representing a single clause of the search to be composed.
    """
    length, filter_type, type_tag, value, exclude = [
        query_dict[k] for k in ['length', 'filter_type', 'type_tag', 'value', 'exclude']
    ]

    query_data = {}

    if length == 'short':
        query_data['searchablestring__type_tag'] = type_tag

    else:
        query_data['longsearchablestring__type_tag'] = type_tag

    if filter_type == 'text_search':
        query_data['longsearchablestring__searchable_value'] = SearchQuery(
            value,
            config='spanish',
        )
    else:
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


def search_query_data_to_result_queryset(dataset, search_data_query):
    """
    Given a list of list of dicts validated by query_api.schema.QuerySchema,
    create a list of subqueries (each one consisting of a big JOIN expression
    created with `queries_to_subqueryset`), then combine these into one
    queryset with `.union` (creating one big SQL UNION expression).
    """
    # Create nested list of lists of Q instances
    list_of_qs = [
        [Q(dataset=dataset)] + [
            query_dict_to_q(query_dict)
            for query_dict in sub_clause
        ]
        for sub_clause in search_data_query
        if sub_clause
    ]

    # Transform lists of Q instances into subqueries
    list_of_subquerysets = [queries_to_subqueryset(queries) for queries in list_of_qs]

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
    )

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
