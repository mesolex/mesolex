from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.template.response import TemplateResponse
from django.urls import path

from lexicon import models


class CitationMediaAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        citation_urls = [
            path('csv/', self.admin_site.admin_view(self.csv_view))
        ]
        return citation_urls + urls
    
    def csv_view(self, request):
        return TemplateResponse(request, 'admin/citation_media_csv.html', {})


class LexicalEntryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }


admin.site.register(models.CitationMedia, CitationMediaAdmin)
admin.site.register(models.LexicalEntry, LexicalEntryAdmin)
