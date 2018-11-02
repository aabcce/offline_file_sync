# coding=utf-8

from __future__ import unicode_literals

from django.db import models

class File(models.Model):
    class Meta:
        managed = False
        db_table = "file"

    ID = models.AutoField(primary_key=True)
    FOLDER = models.CharField(max_length=512)
    FILE = models.CharField(max_length=512)
    ERROR_STATE = models.IntegerField()
    CTMP = models.FloatField()
    MTMP = models.FloatField()
    FSIZE = models.IntegerField()
    HASH = models.CharField(max_length=32)

    def toDict(self):
        return dict([(attr, getattr(self, attr)) for attr in
                     [f.name for f in self._meta.fields]])  # type(self._meta.fields).__name__