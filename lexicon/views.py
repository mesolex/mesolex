from django.shortcuts import render

from haystack.generic_views import SearchView

from .forms import LexiconSearchForm


def home(request):
    return render(request, 'home.html', {})


class LexiconSearchView(SearchView):
    form_class = LexiconSearchForm
