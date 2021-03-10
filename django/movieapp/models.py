# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.db import connection

from .crawler import Crawler, LinkType

import logging

logger = logging.getLogger('debug')

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

# May not be appropriate in some cases e.g. duplicate names
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

def get_link_ids_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT imdbId, tmdbId
            FROM movies
            WHERE movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result[0] if result else ["N/A", "N/A"]

def get_movieID_by_title(movie_title):
    #find movieID based on movie title 
    query = '''select movieID from movies where movieTitle = %s'''
    with connection.cursor() as cursor:
        cursor.execute(query, [movie_title.strip()])
        row = cursor.fetchall()
        return row # row[0][0]

def get_table_row_number(table_name):
    query = 'SELECT COUNT(*) FROM ' + table_name
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchall()
        return row

def get_released_year_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT movieReleased
            FROM movies
            WHERE movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result[0][0] if result else None

def get_movie_id_list():
    query = '''
            SELECT movieID
            FROM movies;
            '''
    result = execute_query(query)
    return result

def get_ratings_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT ratingFigure
            FROM ratings
            WHERE movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result if result else []

def get_movie_name_by_movie_id(movie_id):
    if not movie_id:
        return None
    query = '''
            SELECT movieTitle
            FROM movies
            WHERE movieID = %s;
            '''
    result = execute_query(query, [movie_id])
    return result if result else []

def get_imdb_img(movie_id, movie_title):
    crawler = Crawler(movie_id, movie_title, LinkType.IMDB)
    if crawler:
        return crawler.get_imdb_img_url()
    else:
        return "" 
    
def get_summary_text(movie_id, movie_title):
    crawler = Crawler(movie_id, movie_title, LinkType.IMDB)
    if crawler:
        logger.info("HTML found!")
        return crawler.get_summary_context()
    else:
        logger.info("NOT found!")
        return "" 

def determine_polarizition(ratings):
    polarized = False

    number_of_ratings = len(ratings)
    if number_of_ratings == 0:
        return polarized, 0, 0,

    ratings_list = list(ratings)

    good_ratings = sum(float(rating[0]) >= 4 for rating in ratings_list)
    bad_ratings = sum(float(rating[0]) <= 2 for rating in ratings_list)
    
    good_ratio = good_ratings/number_of_ratings
    bad_ratio = bad_ratings/number_of_ratings

    if (good_ratio >= 0.45 and bad_ratio >= 0.45):
        polarized = True
    
    

    return polarized, good_ratio*100, bad_ratio*100

def determine_polarization2(movie_id):
    query = '''
            SELECT g, b, (g/(g+b)) AS goodRatio, (b/(g+b)) AS badRatio
            FROM 
                (SELECT COUNT(ratingFigure) AS g
                FROM ratings
                WHERE movieID = '1' AND ratingFigure >= 4) AS goodRatings,
                (SELECT COUNT(ratingFigure) AS b
                FROM ratings
                WHERE movieID = '1' AND ratingFigure <= 2) AS badRatings;

            '''
    result = execute_query(query, [movie_id])
    

def get_prediction_movies_row_number():
    query = '''
            SELECT COUNT(*)
            FROM movies
            WHERE movieReleased = 0
            '''
    result = execute_query(query)
    return result[0][0]

def get_limited_movies(limit):
    query = '''
            SELECT movieID
            FROM movies
            LIMIT %s, 20;
            '''
    result = execute_query(query, [limit])
    return result

def total_number_of_movies():
    query = '''
            SELECT COUNT(movieID)
            FROM movies;
            '''
    result = execute_query(query)
    return result

def gather_user_groups(movie_id):
    query1 = '''
            SELECT * 
            FROM 
                (SELECT COUNT(userID) AS like_total 
                    FROM ratings 
                    WHERE movieID = %s AND ratingFigure >= 4) AS likers,
                (SELECT COUNT(userID) AS dislike_total 
                    FROM ratings 
                    WHERE movieID = %s AND ratingFigure <= 2) AS haters;
            '''
    counts = execute_query(query1, [movie_id,movie_id])

    query2 = '''
            SELECT userID
            FROM ratings
            WHERE movieID = %s AND ratingFigure >= 4;
            '''
    result2 = execute_query(query2, [movie_id])

    query3 = '''
            SELECT userID
            FROM ratings
            WHERE movieID = %s AND ratingFigure <= 2;
            '''
    result3 = execute_query(query3, [movie_id])

    return counts, result2, result3

def preference_by_tag(tag):
    likers = '''
            SELECT ratings.userID
            FROM
                ratings,
                (SELECT userTagsMovie.userID, userTagsMovie.movieID
                    FROM 
                        userTagsMovie
                    INNER JOIN 
                            (SELECT tagID
                            FROM tags 
                            WHERE tagName = %s) AS selected_tagID
                    ON userTagsMovie.tagID = selected_tagID.tagID) AS associated_user_movie_ID
            WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.movieID = associated_user_movie_ID.movieID AND ratings.ratingFigure >= 4
            GROUP BY ratings.userID;
            '''
    likers_list = execute_query(likers, [tag])

    haters = '''
            SELECT ratings.userID
            FROM
                ratings,
                (SELECT userTagsMovie.userID, userTagsMovie.movieID
                    FROM 
                        userTagsMovie
                    INNER JOIN 
                            (SELECT tagID
                            FROM tags 
                            WHERE tagName = %s) AS selected_tagID
                    ON userTagsMovie.tagID = selected_tagID.tagID) AS associated_user_movie_ID
            WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.movieID = associated_user_movie_ID.movieID AND ratings.ratingFigure <= 2
            GROUP BY ratings.userID;
            '''
    haters_list = execute_query(haters, [tag])
    return likers_list, haters_list

def general_preference_by_tag(tag):
    likers = '''
            SELECT ratings.userID
                FROM
                    ratings,
                    (SELECT userTagsMovie.userID
                        FROM 
                            userTagsMovie
                        INNER JOIN 
                                (SELECT tagID
                                FROM tags 
                                WHERE tagName = %s) AS selected_tagID
                        ON userTagsMovie.tagID = selected_tagID.tagID) AS associated_user_movie_ID
                WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.ratingFigure >= 4
                GROUP BY ratings.userID;
            '''
    likers_list = execute_query(likers, [tag])

    haters = '''
            SELECT ratings.userID
                FROM
                    ratings,
                    (SELECT userTagsMovie.userID
                        FROM 
                            userTagsMovie
                        INNER JOIN 
                                (SELECT tagID
                                FROM tags 
                                WHERE tagName = %s) AS selected_tagID
                        ON userTagsMovie.tagID = selected_tagID.tagID) AS associated_user_movie_ID
                WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.ratingFigure <= 2
                GROUP BY ratings.userID;
            '''
    haters_list = execute_query(haters, [tag])

    return likers_list, haters_list