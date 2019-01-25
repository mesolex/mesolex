import csv
import io
import logging
from prettyjson import PrettyJSONWidget

from django import forms
from django.contrib import admin, messages
from django.contrib.postgres.fields import JSONField
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from lexicon import models


logger = logging.getLogger(__name__)


CSV_FIELDS = [
    'Path',
    'UID',
    'Filename',
]


class MediaCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        help_text="Upload a CSV file with the columns 'Path', 'UID', and 'Filename'."
    )
    csv_file.label = 'CSV File'

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        decoded = io.StringIO(csv_file.read().decode('utf-8'))
        reader = csv.DictReader(decoded, fieldnames=CSV_FIELDS)
        rows = [row for row in reader]

        if len(rows) == 0 or len(rows[1]) > len(CSV_FIELDS):
            raise forms.ValidationError('Problem with CSV format.')

        return rows[1:]


class MediaAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        citation_urls = [
            path('csv/', self.admin_site.admin_view(self.csv_view))
        ]
        return citation_urls + urls
    
    def csv_view(self, request):
        if request.method == 'POST':
            form = MediaCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                errors = 0
                updated = 0
                created = 0
                for item in form.cleaned_data['csv_file']:
                    try:
                        entry = models.LexicalEntry.objects.get(_id=str(item['UID']).zfill(5))
                        (_, _created) = models.Media.objects.update_or_create(
                            entry=entry,
                            defaults={
                                'mime_type': 'audio/mpeg',
                                'url': item['Path'] + item['Filename'],
                            },
                        )
                        if _created:
                            created += 1
                        else:
                            updated += 1
                    except:
                        logger.exception("Error adding media file with UID {uid}".format(uid=item['uid']))
                        errors += 1
                
                messages.add_message(
                    request,
                    messages.INFO,
                    'CSV submitted: {created} created, {updated} updated, {errors} errors.'.format(
                        created=created,
                        updated=updated,
                        errors=errors,
                    )
                )
                    
                return HttpResponseRedirect(reverse('admin:lexicon_media_changelist'))

            return TemplateResponse(request, 'admin/citation_media_csv.html', {
                'form': form,
            })

        return TemplateResponse(request, 'admin/citation_media_csv.html', {
            'form': MediaCSVUploadForm()
        })


class LexicalEntryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }


admin.site.register(models.Media, MediaAdmin)
admin.site.register(models.LexicalEntry, LexicalEntryAdmin)
