from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from lexicon import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(
            'Indexing {count} searchable strings'.format(
                count=models.LongSearchableString.objects.count(),
            ),
        )

        models.LongSearchableString.objects.update(
            searchable_value=SearchVector(
                'value',
                config='spanish',
            ),
        )
