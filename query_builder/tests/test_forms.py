from unittest.mock import MagicMock

import django.forms
from django.db.models import Q
from django.test import TestCase

from query_builder import forms


class QueryBuilderFormTestCase(TestCase):
    def test_applies_transformations(self):
        """
        For a subclass of the QueryBuilderForm, check that:

        - All of the functions in its ``transformations`` get called
        - The output of one determines the input to the next
        """
        fake_transformation = MagicMock(return_value=('__something_else', 'baz'))
        fake_transformation_two = MagicMock(return_value=('__icontains', 'foo'))
        class TestFormSubclass(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('bar', 'Bar',),
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
            'filter_on': 'bar'
        }

        instance = TestFormSubclass(data=data)
        self.assertTrue(instance.is_valid())
        
        instance.get_filter_action_and_query()  # value not needed!
        self.assertTrue(fake_transformation.called)
        self.assertTrue(fake_transformation_two.called)
        self.assertEqual(
            ('contains', '__icontains', 'foo', data),
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
                ('bar', 'Bar',),
            ]
            FILTERABLE_FIELDS_DICT = {
                'bar': ('bar', ),
            }

        test_formset = django.forms.formset_factory(
            TestForm,
            formset=forms.QueryBuilderBaseFormset,
        )

        formset_data = {
            "form-0-query_string": "foo1",
            "form-0-operator": "and",
            "form-0-filter": "begins_with",
            "form-0-filter_on": "bar",
            
            "form-1-query_string": "foo2",
            "form-1-operator": "and",
            "form-1-filter": "begins_with",
            "form-1-filter_on": "bar",

            "form-2-query_string": "foo3",
            "form-2-operator": "or",
            "form-2-filter": "begins_with",
            "form-2-filter_on": "bar",

            "form-3-query_string": "foo4",
            "form-3-operator": "and",
            "form-3-filter": "begins_with",
            "form-3-filter_on": "bar",

            "form-4-query_string": "foo5",
            "form-4-operator": "and",
            "form-4-filter": "begins_with",
            "form-4-filter_on": "bar",

            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-MIN_NUM_FORMS": "0",
            "form-TOTAL_FORMS": "5",
        }

        bound_formset = test_formset(formset_data)

        self.assertTrue(bound_formset.is_valid())

        query = bound_formset.get_full_query()

        # Expected bracketing: (foo1 & foo2) | (foo3 & foo4 & foo5)
        self.assertEqual(
            'OR',
            query.connector,
        )

        branch_1 = query.children[0]
        branch_2 = query.children[1]

        self.assertEqual(2, len(branch_1))
        self.assertEqual(3, len(branch_2))

        self.assertEqual('AND', branch_1.connector)
        self.assertEqual('AND', branch_2.connector)

        self.assertEqual(
            [
                ('bar__istartswith', 'foo1'),
                ('bar__istartswith', 'foo2'),
            ],
            branch_1.children,
        )
        self.assertEqual(
            [
                ('bar__istartswith', 'foo3'),
                ('bar__istartswith', 'foo4'),
                ('bar__istartswith', 'foo5'),
            ],
            branch_2.children,
        )

    def test_works_without_global_filters(self):
        class TestForm(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('bar', 'Bar',),
            ]
            FILTERABLE_FIELDS_DICT = {
                'bar': ('bar', ),
            }

        test_formset = django.forms.formset_factory(
            TestForm,
            formset=forms.QueryBuilderBaseFormset,
        )

        formset_data = {
            "form-0-query_string": "foo",
            "form-0-operator": "and",
            "form-0-filter": "begins_with",
            "form-0-filter_on": "bar",
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-MIN_NUM_FORMS": "0",
            "form-TOTAL_FORMS": "1",
        }

        bound_formset = test_formset(formset_data)

        self.assertTrue(bound_formset.is_valid())
        
        query = bound_formset.get_full_query()

        self.assertEqual(
            [('bar__istartswith', 'foo')],
            query.children,
        )

    def test_applies_global_filters(self):
        class TestForm(forms.QueryBuilderForm):
            FILTERABLE_FIELDS = [
                ('bar', 'Bar',),
            ]
            FILTERABLE_FIELDS_DICT = {
                'bar': ('bar', ),
            }

        class TestGlobalFilter(forms.QueryBuilderGlobalFiltersForm):
            foo_bar = django.forms.BooleanField(required=False)
            baz_qux = django.forms.BooleanField(required=False)
            
            def clean_foo_bar(self):
                foo_bar = self.cleaned_data['foo_bar']
                return Q(baz__isnull=(not foo_bar))

            def clean_baz_qux(self):
                baz_qux = self.cleaned_data['baz_qux']
                return Q(qux__isnull=(baz_qux))

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
            "form-0-filter_on": "bar",
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-MIN_NUM_FORMS": "0",
            "form-TOTAL_FORMS": "1",
            "foo_bar": "on",
            "baz_qux": "on",
        }

        bound_formset = test_formset(formset_data)

        self.assertTrue(bound_formset.is_valid())
        
        query = bound_formset.get_full_query()

        self.assertEqual(3, len(query.children))
        self.assertEqual('AND', query.connector)
        self.assertIn(
            ('baz__isnull', False),
            query.children,
        )
        self.assertIn(
            ('qux__isnull', True),
            query.children,
        )
