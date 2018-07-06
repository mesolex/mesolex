from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from lexicon import models


class LexicalEntryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }


admin.site.register(models.LexicalEntry, LexicalEntryAdmin)
