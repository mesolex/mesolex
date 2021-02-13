import json

from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from lexicon.forms import formset_for_lg
from mesolex.config import LANGUAGES
from mesolex.utils import ForceProxyEncoder, get_default_data_for_lg


class SearchContextBuilder:
    @staticmethod
    def search_context(request, context):
        formset_class = formset_for_lg(request.GET.get('dataset'))
        formset = formset_class(request.GET)

        try:
            query = formset.get_full_query()
        except ValidationError:
            # The formset has been tampered with.
            # Django doesn't handle this very gracefully.
            # To prevent a 500 error, just bail out here.
            # TODO: make this nicer.
            return {**context, **SearchContextBuilder.search_query_data(formset_class())}

        lexical_entries = query.distinct().order_by('value')

        paginator = Paginator(lexical_entries, 25)
        result_page = request.GET.get('page', 1)

        try:
            display_entries = paginator.page(result_page)
        except PageNotAnInteger:
            display_entries = paginator.page(1)
        except EmptyPage:
            display_entries = paginator.page(paginator.num_pages)
            result_page = paginator.num_pages

        return {
            **context,
            **SearchContextBuilder.search_query_data(
                formset,
                display_entries=display_entries,
                paginator=paginator,
                result_page=result_page,
            ),
        }

    @staticmethod
    def search_query_data(
            formset,
            display_entries=None,
            paginator=None,
            result_page=1,
    ):
        return {
            'lexical_entries': display_entries,
            'num_pages': paginator.num_pages if paginator else 0,
            'num_entries': paginator.count if paginator else 0,
            'result_page': result_page,
            'query': True,
            'languages': json.dumps(
                LANGUAGES,
                ensure_ascii=False,
                cls=ForceProxyEncoder,
            ),
            'search': {
                'formset': formset,
                'formset_global_filters_form': formset.global_filters_form,
                'formset_data': json.dumps([form.cleaned_data for form in formset.forms]),
                'formset_global_filters_form_data': json.dumps(formset.global_filters_form.data),
                'formset_datasets_form': formset.datasets_form,
                'formset_datasets_form_data': json.dumps(formset.datasets_form.data),
                'formset_errors': json.dumps(formset.errors),
            },
            'language': formset.data.get('dataset', 'azz'),
        }

    @staticmethod
    def default_context(request, context):
        formset = formset_for_lg(None)()

        context['languages'] = json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        )

        context['search'] = {
            'formset': formset,
            'formset_datasets_form_data': json.dumps([]),
            'formset_global_filters_form_data': json.dumps([]),
            'formset_data': json.dumps(get_default_data_for_lg(None)),
            'formset_errors': json.dumps([]),
        }

        return context

    @staticmethod
    def get_context(request):
        context = {}

        if request.GET:
            return SearchContextBuilder.search_context(request, context)

        return SearchContextBuilder.default_context(request, context)
