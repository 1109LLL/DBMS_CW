# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.db import connection


class Movie(models.Model):
    movieID = models.CharField("movieID", max_length=255, blank = True, null = True)
    title = models.CharField("titlle", max_length=255, blank = True, null = True)


    def __str__(self):
        return self.movieID