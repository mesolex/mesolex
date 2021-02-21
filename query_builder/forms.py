import json
import operator
import re
from collections import namedtuple
from functools import reduce
from typing import List

from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from lexicon.models import Entry, SearchableString, LongSearchableString
from mesolex.utils import ForceProxyEncoder, contains_word_to_regex


class CombiningQueryset(namedtuple(
        'CombiningQueryset',
        ['operator', 'queryset'],
)):
    """
    Helper structure to hold queryset data as it is composed
    together into its final form.
    """


class QuerysetGrouper:
    """
    Helper class to compose together querysets in a way that
    respects operator precedence.
    """

    def __init__(self, queries=None):
        self._querysets = [] if queries is None else queries

    def append(self, val: CombiningQueryset):
        self._querysets.append(val)

    @staticmethod
    def _handle_next_and(accumulator, next_cq: CombiningQueryset):
        """
        Reducer function to multiply together all querysets
        tagged with the "and" operator. This ensures that "and"
        binds tighter; "or" can be handled in a second cleanup
        reduction.
        """
        (querysets, and_tree) = accumulator
        if next_cq.operator == 'and':
            and_tree = and_tree.intersection(next_cq.queryset)
        else:
            querysets = [*querysets, and_tree]
            and_tree = next_cq.queryset
        return (querysets, and_tree)

    @staticmethod
    def _group_ands(querysets: List[CombiningQueryset]):
        (querysets, and_tree) = reduce(
            QuerysetGrouper._handle_next_and,
            querysets,
            ([], Entry.objects.all()),
        )
        return [*querysets, and_tree]

    @property
    def combined_queryset(self):
        return reduce(
            lambda acc, q: acc.union(q),
            QuerysetGrouper._group_ands(self._querysets)
        )


class QueryBuilderForm(forms.Form):
    BOOLEAN_OPERATORS = (
        ('and', 'y'),
        ('or', 'o'),
        ('and_n', 'y no'),
        ('or_n', 'o no'),
    )

    FILTERS = (
        ('begins_with', _('Empieza con')),
        ('ends_with', _('Termina con')),
        ('contains', _('Contiene secuencia')),
        ('contains_word', _('Contiene palabra')),
        ('exactly_equals', _('Es exactamente igual a')),
        ('regex', _('Expresión regular')),
        ('text_search', _('Coincide con')),
    )

    FILTERS_DICT = {
        'begins_with': '__startswith',
        'ends_with': '__endswith',
        'contains': '__contains',
        'contains_word': '__regex',
        'exactly_equals': '',
        'regex': '__regex',
        'text_search': None,
    }

    # NOTE: abstract, must be filled in with sequence of pairs,
    # e.g. ``('lemma', _('Entrada'))``
    FILTERABLE_FIELDS = []

    # NOTE: abstract, must be filled in with dictionary
    # enumerating the fields to touch with a given query
    # field, e.g. ``'lemma': ('lemma', 'variant__value')``.
    FILTERABLE_FIELDS_DICT = {}

    # NOTE: abstract, must be filled in with dictionary
    # matching elasticsearch quasi-filters and lists
    # of index fields
    ELASTICSEARCH_FIELDS = []
    ELASTICSEARCH_FIELDS_DICT = {}

    query_string = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    operator = forms.ChoiceField(
        choices=BOOLEAN_OPERATORS,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )
    filter = forms.ChoiceField(
        choices=FILTERS,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filter_on'] = forms.ChoiceField(
            choices=self.FILTERABLE_FIELDS + self.ELASTICSEARCH_FIELDS,
            widget=forms.Select(attrs={'class': 'custom-select'})
        )

    @property
    def transformations(self):
        """
        A sequence of transformations to apply to the form data to
        produce the final filter action and query.

        Although most filters have a "direct" interpretation in
        ORM terms (for example, "starts with" translates to "__istartswith"),
        some don't: "contains word", for example, needs to be
        translated into some kind of regular expression.

        The types of transformations that have to be applied are
        domain-specific, and each subclass of QueryBuilderForm
        can modify or add to the sequence of transformations.
        For example, the lexicon search form for Nahuat data
        includes a "vowel length neutralization" transformation.

        Each transformation expects four arguments:

        - filter_name (e.g. "contains_word")
        - filter_action (e.g. "__iregex")
        - query_string (e.g. "ta:ni")
        - form_data (a dict of cleaned form data)

        Each transformation returns a tuple containing the
        new filter action and the new query string (both of which
        may be the same as the input!).
        """
        return [
            contains_word_to_regex,
        ]

    def get_filter_action_and_query(self):
        """
        NOTE: this will have to be overridden if anything interesting
        is done to generate a query string and filter action beyond
        what can be done with the "transformations" feature.
        """

        if not self.is_bound:
            return (None, None)

        form_data = self.cleaned_data
        filter_name = form_data['filter']
        filter_action = self.FILTERS_DICT.get(filter_name, '')
        query_string = form_data['query_string']

        for transformation in self.transformations:
            (filter_action, query_string) = transformation(
                filter_name,
                filter_action,
                query_string,
                form_data,
            )

        return (filter_action, query_string)

    def _get_db_queryset(self, exclude=False):
        (filter_action, query_string) = self.get_filter_action_and_query()
        filter_on_str = self.cleaned_data['filter_on']
        filter_on_vals = self.FILTERABLE_FIELDS_DICT.get(filter_on_str, [])

        query_expressions = []

        for filter_on_val in filter_on_vals:
            # If the filter_on_val is a dict, it will have the form:
            # { 'length': 'long', 'tag': 'definition' }
            # { 'length': 'short', 'tag': 'root' }
            if isinstance(filter_on_val, dict):
                if filter_on_val.get("length") == "long":
                    string_class = LongSearchableString
                else:
                    string_class = SearchableString
                string_query_expression = Q(**{
                    f'type_tag': filter_on_val.get('tag'),
                    f'value{filter_action}': query_string,
                })
                matching_strings = (
                    string_class.objects
                    .filter(string_query_expression)
                    .values("entry")
                    .distinct()
                )
                query_expressions.append(Q(pk__in=[
                    matching_string['entry'] for matching_string in matching_strings
                ]))
            # If it is a string, then it is just the name of a field on
            # the model
            else:
                query_expressions.append(Q(**{'%s%s' % (filter_on_val, filter_action): query_string}))

        if exclude:
            return reduce(
                lambda acc, q: acc.intersection(q),
                [Entry.objects.exclude(q) for q in query_expressions],
            )

        return reduce(
            lambda acc, q: acc.union(q),
            [Entry.objects.filter(q) for q in query_expressions],
        )

    def _get_es_queryset(self, exclude=False):
        query_fields = self.ELASTICSEARCH_FIELDS_DICT.get(self.cleaned_data['filter_on'])
        results = self.DocumentClass.search().query(
            'multi_match',
            query=self.cleaned_data['query_string'],
            fields=query_fields,
        ).scan()

        if exclude:
            return Q(pk__not__in=[result.meta.id for result in results])

        return Q(pk__in=[result.meta.id for result in results])

    def get_queryset(self, exclude=False):
        if not self.is_bound:
            return Entry.objects.all()

        if self.cleaned_data['filter_on'] in [field[0] for field in self.ELASTICSEARCH_FIELDS]:
            return self._get_es_queryset(exclude=exclude)

        return self._get_db_queryset(exclude=exclude)

    def clean(self):
        cleaned_data = super().clean()
        if 'filter' in cleaned_data and cleaned_data['filter'] == 'regex':
            qs = cleaned_data['query_string']
            try:
                re.compile(qs)
            except Exception:
                self.add_error(
                    'query_string',
                    forms.ValidationError(_('Expresión regular no válida.')),
                )


class QueryBuilderGlobalFiltersForm(forms.Form):
    # NOTE: this is just an abstract placeholder for concrete classes
    # to be used by subclasses of QueryBuilderBaseFormset.
    # The idea is that this form is a sidekick of the formset that
    # represents "global" filters that get intersected with the
    # filters represented by the formset components at the end
    # of the query-composition process.
    pass


class QueryBuilderDatasetsForm(forms.Form):
    dataset = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )


class QueryBuilderBaseFormset(forms.BaseFormSet):
    global_filters_class = QueryBuilderGlobalFiltersForm
    datasets_class = QueryBuilderDatasetsForm

    # NOTE: abstract, must be filled in with sequence of pairs,
    # e.g. ``('lemma', _('Entrada'))``
    FILTERABLE_FIELDS = []

    # NOTE: abstract, must be filled in with dictionary of
    # controlled vocabulary fields and their pair values.
    CONTROLLED_VOCAB_FIELDS = {}

    # NOTE: abstract, must be filled in with list of
    # fields that are searched with the search engine backend.
    TEXT_SEARCH_FIELDS = []

    # Available for overriding if fields must
    # be computed dynamically.
    @property
    def filterable_fields(self):
        return self.FILTERABLE_FIELDS

    @property
    def controlled_vocab_fields(self):
        return self.CONTROLLED_VOCAB_FIELDS

    @property
    def text_search_fields(self):
        return self.TEXT_SEARCH_FIELDS

    @property
    def configuration_data(self):
        config = {
            'controlled_vocab_fields': self.controlled_vocab_fields,
            'filterable_fields': self.filterable_fields,
            'text_search_fields': self.text_search_fields,
        }
        return config

    @property
    def configuration_data_as_json(self):
        return json.dumps(
            self.configuration_data,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.global_filters_form = self.global_filters_class(*args, **kwargs)
        self.datasets_form = self.datasets_class(*args, **kwargs)

    def get_full_queryset(self):
        """
        Using a QuerysetGrouper, combine the querysets returned by each
        individual form's `get_queryset` method.
        """
        queryset_group = QuerysetGrouper()

        for form in self.forms:
            if form.is_valid():
                form_operator = form.cleaned_data['operator']

                # If the form operator is a "not" variant ("and not", "or not"),
                # get the queryset in its "exclude" form, then translate the
                # operator into its positive variant so it can be combined normally.
                if form_operator in ('and_n', 'or_n'):
                    form_q = form.get_queryset(exclude=True)
                    form_operator = form_operator.replace('_n', '')
                else:
                    form_q = form.get_queryset()

                # Intersect the form's queryset with the queryset returned by
                # any global filters.
                if self.global_filters_form.is_valid() and form_q:
                    for (_name, global_filter,) in self.global_filters_form.cleaned_data.items():
                        form_q = form_q.intersection(global_filter)

                queryset_group.append(CombiningQueryset(
                    operator=form_operator,
                    queryset=form_q,
                ))

        return queryset_group.combined_queryset
