# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.db import connection


class Movie(models.Model):
    movieID = models.CharField("movieID", max_length=255, blank = True, null = True)
    title = models.CharField("title", max_length=255, blank = True, null = True)


    def __str__(self):
        return self.movieID

def get_avg_rating_by_movie_id(movie_id):
    query = '''
            SELECT AVG(ratingFigure)
            FROM ratings
            WHERE movieID = %s;
            '''
    with connection.cursor() as cursor:
        cursor.execute(query, [movie_id])
        row = cursor.fetchall()
        return row

    return None