from django.db import models


class SoundMetadata(models.Model):
    fn_sound = models.CharField(max_length=256, blank=True)
    fn_trans = models.CharField(max_length=256, blank=True)
    project = models.CharField(max_length=64, blank=True)
    uid = models.CharField(max_length=64, blank=True)
    filepast = models.CharField(max_length=64, blank=True)
    folder = models.CharField(max_length=64, blank=True)
    duration = models.CharField(max_length=64, blank=True)
    size = models.CharField(max_length=64, blank=True)
    wordcount = models.CharField(max_length=64, blank=True)
    encyxref = models.CharField(max_length=64, blank=True)
    encyref2 = models.CharField(max_length=64, blank=True)

    # languageGroup
    language = models.CharField(max_length=64, blank=True)
    lg_var = models.CharField(max_length=64, blank=True)
    lg_code = models.CharField(max_length=8, blank=True)
    
    lgvil = models.CharField(max_length=64, blank=True)
    lg_mpio = models.CharField(max_length=64, blank=True)
    lg_state = models.CharField(max_length=64, blank=True)
    lg_country = models.CharField(max_length=64, blank=True)
    # NOTE: also lgcountry

    # recordbyGroup
    recordby = models.CharField(max_length=64, blank=True)
    date = models.DateField(null=True, blank=True)
    tracks = models.CharField(max_length=64, blank=True)
    
    rec_format = models.CharField(max_length=64, blank=True)
    rec_orig = models.CharField(max_length=64, blank=True) # NOTE: also recorig
    rec_machine = models.CharField(max_length=64, blank=True)
    rec_mike = models.CharField(max_length=64, blank=True)
    rec_power = models.CharField(max_length=64, blank=True)
    contr1 = models.CharField(max_length=64, blank=True)
    con1_role = models.CharField(max_length=64, blank=True)
    con1_sex = models.CharField(max_length=64, blank=True)
    con1_origin = models.CharField(max_length=64, blank=True)
    con1_track = models.CharField(max_length=64, blank=True)
    contr2 = models.CharField(max_length=64, blank=True)
    con2_role = models.CharField(max_length=64, blank=True)
    con2_sex = models.CharField(max_length=64, blank=True)
    con2_origin = models.CharField(max_length=64, blank=True)
    con2_track = models.CharField(max_length=64, blank=True)

    # genreGroup
    genre = models.CharField(max_length=64, blank=True)
    subgenre = models.CharField(max_length=64, blank=True)
    
    titnative = models.CharField(max_length=64, blank=True)
    titspn = models.CharField(max_length=64, blank=True)
    titeng = models.CharField(max_length=64, blank=True)
    descrip = models.TextField(blank=True)
    native_prim = models.CharField(max_length=64, blank=True) # native-prim
    sci_prim = models.CharField(max_length=64, blank=True) # sci-prim
    sci_second = models.CharField(max_length=64, blank=True) # sci-second
    transby = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=64, blank=True)
    rights = models.CharField(max_length=64, blank=True)
    calidad = models.CharField(max_length=64, blank=True)
    archive = models.CharField(max_length=64, blank=True)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    ref = models.CharField(max_length=64, blank=True)