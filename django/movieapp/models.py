# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.db import connection


class Movie(models.Model):
    movieID = models.CharField("movieID", max_length=255, blank = True, null = True)
    title = models.CharField("title", max_length=255, blank = True, null = True)


    def __str__(self):
        return self.movieID

def execute_query(query, params=[]):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchall()
        return row
    return None

def get_avg_rating_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT AVG(ratingFigure)
            FROM ratings
            WHERE movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result[0][0] if result else 'N/A'

# May not be appropriate in some cases e.g. dumplicate names
def get_movie_id_by_title(movie_title):
    if not movie_title:
        return None
    query = '''
            SELECT movieID
            FROM movies
            WHERE movieTitle = %s;
            '''
    result = execute_query(query, [movie_title])
    return result[0][0] if result else None

def get_tag_names_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT t.tagName
            FROM tags AS t, userTagsMovie AS utm
            WHERE t.tagID = utm.tagID AND utm.movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result if result else []

def get_imdb_link_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT imdbId
            FROM movies
            WHERE movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result[0][0] if result else None