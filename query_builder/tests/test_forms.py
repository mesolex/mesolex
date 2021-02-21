from unittest.mock import MagicMock

import django.forms
from django.db.models import Q
from django.test import TestCase

from lexicon.models import Entry
from query_builder import forms


class QueryGrouperTestCase(TestCase):
    def test_respects_operator_precedence(self):
        """
        The QueryGrouper helper class should respect operator
        precedence by binding "and" tighter than "or" when
        combining queries.

        For example, "foo1 & foo2 | foo3 & foo4 & foo5" should
        be bracketed as "(foo1 & foo2) | (foo3 & foo4 & foo5)",
        rather than as (for example) "(((foo1 & foo2) | foo3) & foo4) & foo5".
        """
        included = [
            Entry.objects.create(value='abcde', identifier='abcde'),
            Entry.objects.create(value='abcd', identifier='abcd'),
            Entry.objects.create(value='bcde', identifier='bcde'),
        ]
        _not_included = [
            Entry.objects.create(value='abc', identifier='abc'),
            Entry.objects.create(value='ab', identifier='ab'),
            Entry.objects.create(value='cde', identifier='cde'),
            Entry.objects.create(value='de', identifier='de'),
        ]
        grouper = forms.QueryGrouper([
            forms.CombiningQuery('and', Q(value__startswith='abcd')),
            forms.CombiningQuery('and', Q(value__startswith='abc')),
            forms.CombiningQuery('or', Q(value__endswith='bcde')),
            forms.CombiningQuery('and', Q(value__endswith='cde')),
        ])
        query = grouper.combined_query

        self.assertEqual(
            {q.value for q in query},
            {e.value for e in included},
        )


class QueryBuilderFormTestCase(TestCase):
    def test_applies_transformations(self):
        """
        For a subclass of the QueryBuilderForm, check that:

        - All of the functions in its ``transformations`` get called
        - The output of one determines the input to the next
        """
        fake_transformation = MagicMock(return_value=('__something_else', 'baz'))
        fake_transformation_two = MagicMock(return_value=('__contains', 'foo'))

        class TestFormSubclass(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('data__bar', 'Bar',),
            ]

            @property
            def transformations(self):
                return [
                    fake_transformation,
                    fake_transformation_two,
                ]
        data = {
            'query_string': 'foo',
            'operator': 'and',
            'filter': 'contains',
            'filter_on': 'data__bar'
        }

        instance = TestFormSubclass(data=data)
        self.assertTrue(instance.is_valid())

        instance.get_filter_action_and_query()  # value not needed!
        self.assertTrue(fake_transformation.called)
        self.assertTrue(fake_transformation_two.called)
        self.assertEqual(
            ('contains', '__contains', 'foo', data),
            fake_transformation.call_args[0],
        )
        self.assertEqual(
            ('contains', '__something_else', 'baz', data),
            fake_transformation_two.call_args[0],
        )


class QueryBuilderBaseFormsetTestCase(TestCase):
    def test_respects_operator_predence(self):
        """
        When composing together queries specified by the formsets,
        QueryBuilderBaseFormset should respect operator precedence
        by binding AND tighter than OR.

        For example, "foo1 & foo2 | foo3 & foo4 & foo5" should
        be bracketed as "(foo1 & foo2) | (foo3 & foo4 & foo5)",
        rather than as (for example) "(((foo1 & foo2) | foo3) & foo4) & foo5".
        """
        class TestForm(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('data__bar', 'Bar',),
            ]
            FILTERABLE_FIELDS_DICT = {
                'data__bar': ('data__bar', ),
            }

        included = [
            Entry.objects.create(data={'bar': 'abcde'}, identifier='abcde'),
            Entry.objects.create(data={'bar': 'abcd'}, identifier='abcd'),
            Entry.objects.create(data={'bar': 'bcde'}, identifier='bcde'),
        ]
        _not_included = [
            Entry.objects.create(data={'bar': 'abc'}, identifier='abc'),
            Entry.objects.create(data={'bar': 'ab'}, identifier='ab'),
            Entry.objects.create(data={'bar': 'cde'}, identifier='cde'),
            Entry.objects.create(data={'bar': 'de'}, identifier='de'),
        ]

        test_formset = django.forms.formset_factory(
            TestForm,
            formset=forms.QueryBuilderBaseFormset,
        )

        formset_data = {
            "form-0-query_string": "abcd",
            "form-0-operator": "and",
            "form-0-filter": "begins_with",
            "form-0-filter_on": "data__bar",

            "form-1-query_string": "abc",
            "form-1-operator": "and",
            "form-1-filter": "begins_with",
            "form-1-filter_on": "data__bar",

            "form-2-query_string": "bcde",
            "form-2-operator": "or",
            "form-2-filter": "begins_with",
            "form-2-filter_on": "data__bar",

            "form-3-query_string": "cde",
            "form-3-operator": "and",
            "form-3-filter": "begins_with",
            "form-3-filter_on": "data__bar",

            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-MIN_NUM_FORMS": "0",
            "form-TOTAL_FORMS": "4",
        }

        bound_formset = test_formset(formset_data)

        self.assertTrue(bound_formset.is_valid())

        query = bound_formset.get_full_query()

        # Expected bracketing: (foo1 & foo2) | (foo3 & foo4 & foo5)
        self.assertEqual(
            {q.value for q in query},
            {e.value for e in included},
        )

    def test_works_without_global_filters(self):
        class TestForm(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('data__bar', 'Bar',),
            ]
            FILTERABLE_FIELDS_DICT = {
                'data__bar': ('data__bar', ),
            }

        entries = [Entry.objects.create(data={'bar': 'foo'}, identifier='entry1')]

        test_formset = django.forms.formset_factory(
            TestForm,
            formset=forms.QueryBuilderBaseFormset,
        )

        formset_data = {
            "form-0-query_string": "foo",
            "form-0-operator": "and",
            "form-0-filter": "begins_with",
            "form-0-filter_on": "data__bar",
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-MIN_NUM_FORMS": "0",
            "form-TOTAL_FORMS": "1",
        }

        bound_formset = test_formset(formset_data)

        self.assertTrue(bound_formset.is_valid())

        query = bound_formset.get_full_query()

        self.assertEqual(
            set(entries),
            set(query),
        )

    def test_applies_global_filters(self):
        class TestForm(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('data__bar', 'Bar',),
            ]
            FILTERABLE_FIELDS_DICT = {
                'data__bar': ('data__bar', ),
            }

        class TestGlobalFilter(forms.QueryBuilderGlobalFiltersForm):
            include_baz = django.forms.BooleanField(required=False)
            exclude_qux = django.forms.BooleanField(required=False)

            def clean_include_baz(self):
                include_baz = self.cleaned_data['include_baz']
                return Q(data__baz__isnull=(not include_baz))

            def clean_exclude_qux(self):
                exclude_qux = self.cleaned_data['exclude_qux']
                return Q(data__qux__isnull=(exclude_qux))

        class TestFormset(forms.QueryBuilderBaseFormset):
            global_filters_class = TestGlobalFilter

        test_formset = django.forms.formset_factory(
            TestForm,
            formset=TestFormset,
        )

        formset_data = {
            "form-0-query_string": "foo",
            "form-0-operator": "and",
            "form-0-filter": "begins_with",
            "form-0-filter_on": "data__bar",
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-MIN_NUM_FORMS": "0",
            "form-TOTAL_FORMS": "1",
            "include_baz": "on",
            "exclude_qux": "on",
        }

        included = [
            Entry.objects.create(data={'bar': 'foo', 'baz': True}, identifier='entry1'),
        ]

        _excluded = [
            Entry.objects.create(data={'bar': 'foo', 'baz': True, 'qux': True}, identifier='entry2'),
            Entry.objects.create(data={'bar': 'foo', 'qux': True}, identifier='entry3'),
            Entry.objects.create(data={'bar': 'foo'}, identifier='entry4'),
        ]

        bound_formset = test_formset(formset_data)

        self.assertTrue(bound_formset.is_valid())

        query = bound_formset.get_full_query()

        self.assertEqual(
            set(included),
            set(query),
        )
