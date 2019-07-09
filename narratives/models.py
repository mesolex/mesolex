from django.db import models


class SoundMetadata(models.Model):
    fn_sound = models.CharField(max_length=256, blank=True)
    fn_trans = models.CharField(max_length=256, blank=True)
    project = models.CharField(max_length=256, blank=True)
    uid = models.CharField(max_length=256, blank=True)
    filepast = models.TextField(blank=True)
    folder = models.CharField(max_length=256, blank=True)
    duration = models.CharField(max_length=256, blank=True)
    size = models.CharField(max_length=256, blank=True)
    wordcount = models.CharField(max_length=256, blank=True)
    encyxref = models.CharField(max_length=256, blank=True)
    encyref2 = models.CharField(max_length=256, blank=True)

    # languageGroup
    language = models.CharField(max_length=256, blank=True)
    lg_var = models.CharField(max_length=256, blank=True)
    lg_code = models.CharField(max_length=8, blank=True)

    lgvil = models.CharField(max_length=256, blank=True)
    lg_mpio = models.CharField(max_length=256, blank=True)
    lg_state = models.CharField(max_length=256, blank=True)
    lg_country = models.CharField(max_length=256, blank=True)
    # NOTE: also lgcountry

    # recordbyGroup
    recordby = models.CharField(max_length=256, blank=True)
    date = models.DateField(null=True, blank=True)
    tracks = models.CharField(max_length=256, blank=True)

    rec_format = models.CharField(max_length=256, blank=True)
    rec_orig = models.CharField(max_length=256, blank=True) # NOTE: also recorig
    rec_machine = models.CharField(max_length=256, blank=True)
    rec_mike = models.CharField(max_length=256, blank=True)
    rec_power = models.CharField(max_length=256, blank=True)
    contr1 = models.CharField(max_length=256, blank=True)
    con1_role = models.CharField(max_length=256, blank=True)
    con1_sex = models.CharField(max_length=256, blank=True)
    con1_origin = models.CharField(max_length=256, blank=True)
    con1_track = models.CharField(max_length=256, blank=True)
    contr2 = models.CharField(max_length=256, blank=True)
    con2_role = models.CharField(max_length=256, blank=True)
    con2_sex = models.CharField(max_length=256, blank=True)
    con2_origin = models.CharField(max_length=256, blank=True)
    con2_track = models.CharField(max_length=256, blank=True)

    # genreGroup
    genre = models.CharField(max_length=256, blank=True)
    subgenre = models.CharField(max_length=256, blank=True)

    titnative = models.CharField(max_length=512, blank=True)
    titspn = models.CharField(max_length=512, blank=True)
    titeng = models.CharField(max_length=512, blank=True)
    descrip = models.TextField(blank=True)
    native_prim = models.CharField(max_length=256, blank=True) # native-prim
    native_second = models.CharField(max_length=256, blank=True) # native-second
    sci_prim = models.CharField(max_length=256, blank=True) # sci-prim
    sci_second = models.CharField(max_length=256, blank=True) # sci-second
    transby = models.CharField(max_length=256, blank=True)
    status = models.CharField(max_length=256, blank=True)
    rights = models.CharField(max_length=256, blank=True)
    calidad = models.CharField(max_length=256, blank=True)
    archive = models.CharField(max_length=256, blank=True)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    ref = models.CharField(max_length=256, blank=True)

    def __str__(self):
        title = self.titspn if self.titspn else 'Sin titulo'
        return '{title} ({fn_trans})'.format(
            title=title,
            fn_trans=self.fn_trans,
        )
