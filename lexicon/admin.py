from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from lexicon import models


class LexCitationFormInlineAdmin(admin.TabularInline):
    model = models.LexCitationForm


class LexicalEntryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }
    inlines = [
        LexCitationFormInlineAdmin,
    ]


admin.site.register(models.LexicalEntry, LexicalEntryAdmin)
