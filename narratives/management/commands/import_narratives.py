import logging
import xml.etree.ElementTree as ET

from dateutil.parser import parse
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from narratives import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _("Lee una fuente de datos en XML y actualiza la base de datos.")

    def add_arguments(self, parser):
        parser.add_argument('input', type=str)

    def _tx_opt(self, el, tags):
        sub_els = [el.find(tag) for tag in tags if el.find(tag) is not None]
        if len(sub_els) > 0:
            return sub_els[0].text
        return ''

    def _dt_opt(self, el, tags):
        tx = self._tx_opt(el, tags)
        if tx:
            return parse(tx)
        return None

    def handle(self, *args, **options):
        input = options['input']

        tree = ET.parse(input)
        root = tree.getroot()

        updated_entries = 0
        added_entries = 0

        models.SoundMetadata.objects.all().delete()
        sound_groups = root.findall('fn_soundGroup')
        new_models = [models.SoundMetadata(
            fn_sound=self._tx_opt(sound_group, ['fn_sound']),
            fn_trans=self._tx_opt(sound_group, ['fn_trans']),
            project=self._tx_opt(sound_group, ['project']),
            uid=self._tx_opt(sound_group, ['uid']),
            filepast=self._tx_opt(sound_group, ['filepast']),
            folder=self._tx_opt(sound_group, ['folder']),
            duration=self._tx_opt(sound_group, ['duration']),
            size=self._tx_opt(sound_group, ['size']),
            wordcount=self._tx_opt(sound_group, ['wordcount']),
            encyxref=self._tx_opt(sound_group, ['encyxref']),
            encyref2=self._tx_opt(sound_group, ['encyref2']),
            language=self._tx_opt(sound_group, ['languageGroup/language']),
            lg_var=self._tx_opt(sound_group, ['languageGroup/lg_var']),
            lg_code=self._tx_opt(sound_group, ['languageGroup/lg_code']),
            lgvil=self._tx_opt(sound_group, ['lgvil']),
            lg_mpio=self._tx_opt(sound_group, ['lg_mpio']),
            lg_state=self._tx_opt(sound_group, ['lg_state']),
            lg_country=self._tx_opt(sound_group, ['lg_country', 'lgcountry']),
            recordby=self._tx_opt(sound_group, ['recordbyGroup/recordby']),
            date=self._dt_opt(sound_group, ['recordbyGroup/date']),
            tracks=self._tx_opt(sound_group, ['recordbyGroup/tracks']),
            rec_format=self._tx_opt(sound_group, ['rec_format']),
            rec_orig=self._tx_opt(sound_group, ['rec_orig', 'recorig']),
            rec_machine=self._tx_opt(sound_group, ['rec_machine']),
            rec_mike=self._tx_opt(sound_group, ['rec_mike']),
            rec_power=self._tx_opt(sound_group, ['rec_power']),
            contr1=self._tx_opt(sound_group, ['contr1']),
            con1_role=self._tx_opt(sound_group, ['con1_role']),
            con1_sex=self._tx_opt(sound_group, ['con1_sex']),
            con1_origin=self._tx_opt(sound_group, ['con1_origin']),
            con1_track=self._tx_opt(sound_group, ['con1_track']),
            contr2=self._tx_opt(sound_group, ['contr2']),
            con2_role=self._tx_opt(sound_group, ['con2_role']),
            con2_sex=self._tx_opt(sound_group, ['con2_sex']),
            con2_origin=self._tx_opt(sound_group, ['con2_origin']),
            con2_track=self._tx_opt(sound_group, ['con2_track']),
            genre=self._tx_opt(sound_group, ['genreGroup/genre']),
            subgenre=self._tx_opt(sound_group, ['genreGroup/subgenre']),
            titnative=self._tx_opt(sound_group, ['titnative']),
            titspn=self._tx_opt(sound_group, ['titspn']),
            titeng=self._tx_opt(sound_group, ['titeng']),
            descrip=self._tx_opt(sound_group, ['descrip']),
            native_prim=self._tx_opt(sound_group, ['native-prim']),
            sci_prim=self._tx_opt(sound_group, ['sci-prim']),
            sci_second=self._tx_opt(sound_group, ['sci-second']),
            transby=self._tx_opt(sound_group, ['transby']),
            status=self._tx_opt(sound_group, ['status']),
            rights=self._tx_opt(sound_group, ['rights']),
            calidad=self._tx_opt(sound_group, ['calidad']),
            archive=self._tx_opt(sound_group, ['archive']),
            url=self._tx_opt(sound_group, ['url']),
            notes=self._tx_opt(sound_group, ['notes']),
            ref=self._tx_opt(sound_group, ['ref']),
        ) for sound_group in sound_groups]

        models.SoundMetadata.objects.bulk_create(new_models)
