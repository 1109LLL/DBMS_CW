# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.db import connection

from django.core.cache import cache

from .crawler import Crawler, LinkType

from .helpers import *

import logging

logger = logging.getLogger('debug')

# use pre-compiled sql executor
# in order to prevend injections
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
    cache_key = str(movie_id) + "_imdb_img_url"
    img_url_cached = get_cache(cache, cache_key)
    # cache hit, return directly
    if img_url_cached:
        logger.info("cache hit!")
        return img_url_cached
    logger.info("cache miss!")
    # cache miss, crawl and write
    crawler = Crawler(movie_id, movie_title, LinkType.IMDB)
    # not available in imdb
    if not crawler:
        return ""
    img_url = crawler.get_imdb_img_url()
    # only write to cache if found
    if img_url:
        set_cache(cache, cache_key, img_url, 30)
    return img_url 
    
def get_summary_text(movie_id, movie_title):
    crawler = Crawler(movie_id, movie_title, LinkType.IMDB)
    if crawler:
        logger.info("HTML found!")
        return crawler.get_summary_context()
    else:
        logger.info("NOT found!")
        return "" 

def determine_polarization(movie_id):
    polarized = False
    query = '''
            SELECT g, b, (g/(g+b)) AS goodRatio, (b/(g+b)) AS badRatio
            FROM 
                (SELECT COUNT(ratingFigure) AS g
                 FROM ratings
                 WHERE movieID = %s AND ratingFigure >= 4) AS goodRatings,
                (SELECT COUNT(ratingFigure) AS b
<<<<<<< HEAD
                FROM ratings
                WHERE movieID = %s AND ratingFigure <= 2) AS badRatings;
=======
                 FROM ratings
                 WHERE movieID = %s AND ratingFigure <= 2) AS badRatings;
>>>>>>> 6522ea4945620b64d8b05482622962734b2d8712
            '''
    result = execute_query(query, [movie_id, movie_id])
    
    
    if result[0][2] is None or result[0][3] is None:
        return polarized, 0, 0, 0, 0
    else:
        good_ratio = float(format(float(result[0][2])*100, '.1f'))
        bad_ratio = float(format(float(result[0][3])*100, '.1f'))

        if (good_ratio >= 45 and bad_ratio >= 45):
            polarized = True

        g = result[0][0]
        b = result[0][1]
        return polarized, good_ratio, bad_ratio, g, b


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
    ### guarantee to exist and type-correct ###
    return int(result[0][0])

def get_index_movies_info(page=1):
    index = page - 1
    query = '''
            SELECT DISTINCT m.movieID, 
                            m.movieTitle, 
                            m.movieAlias, 
                            m.movieReleased, 
                            GROUP_CONCAT(DISTINCT g.genreName) AS genres
            FROM movies AS m, 
                moviesGenres AS mg, 
                genres AS g
            WHERE mg.movieID = m.movieID
                AND
                g.genreID = mg.genreID
            GROUP BY m.movieID, m.movieTitle, m.movieAlias, m.movieReleased
            LIMIT %s, 20
            ;
            '''
    result = execute_query(query, [index])
    return result

def get_search_movies_info(key="", page=1):
    key = '%' + key + '%'
    query = '''
            SELECT DISTINCT m.movieID, 
                            m.movieTitle, 
                            m.movieAlias, 
                            m.movieReleased, 
                            GROUP_CONCAT(DISTINCT g.genreName) AS genres
            FROM movies AS m, 
                moviesGenres AS mg, 
                genres AS g
            WHERE mg.movieID = m.movieID
                AND
                g.genreID = mg.genreID
                AND
                (
                    m.movieTitle LIKE %s
                OR
                    m.movieAlias LIKE %s
                )
            GROUP BY m.movieID, m.movieTitle, m.movieAlias, m.movieReleased
            LIMIT %s, 20
            ;
            '''
    result = execute_query(query, [key, key, page])
    logger.info(result)
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

# non-null tags, soon to be released, from personality rating tables
def get_personality_qualified_movies():
    query = """
            SELECT DISTINCT m.movieID, m.movieTitle, m.movieAlias, "Coming soon...", GROUP_CONCAT(DISTINCT g.genreName) AS genres
            FROM movies AS m INNER JOIN userMovieRatings AS u
            ON m.movieID = u.movieID,
            genres AS g LEFT JOIN moviesGenres AS mg 
            ON g.genreID = mg.genreID
            WHERE mg.movieID = m.movieID
                AND
                EXISTS (SELECT tagID
                        FROM userTagsMovie AS t
                        WHERE t.movieID = m.movieID)
                AND
                movieReleased = 0
            GROUP BY m.movieID, m.movieTitle, m.movieAlias
            ;
            """
    result = execute_query(query, [])
    return result

def get_personality_user_group_by_movie_id(movie_id):
    query = """
            SELECT b.userID
            FROM movies AS a INNER JOIN userMovieRatings AS b 
            ON a.movieID = b.movieID
            WHERE a.movieID = %s
                  AND 
                  b.predictedRating >= (SELECT AVG(predictedRating)
                                       FROM userMovieRatings
                                       WHERE movieID = a.movieID)
            ;
            """
    result = execute_query(query, [movie_id])
    return result

def get_personality_traits(user_group):
    if not user_group:
        return []
    personalitiy_avgs = []
    query_avg = """
                SELECT AVG({})
                FROM userPersonality;
                """
    for personality in personalities:
        avg = execute_query(query_avg.format(personality), [])[0][0]
        personalitiy_avgs.append(avg)
    query_traits = """
                   SELECT AVG(p.openness) - {0}, 
                          AVG(p.agreeableness) - {1}, 
                          AVG(p.emotionalStability) - {2}, 
                          AVG(p.conscientiousness) - {3}, 
                          AVG(p.extraversion) - {4}
                   FROM userPersonality AS p 
                   WHERE p.userID IN ({5});
                   """
    # safe to format sql string since inputs are from another sql that is safe
    user_group_list = ["\"{0}\"".format(user_tuple[0]) for user_tuple in user_group]
    user_group_str = ",".join(user_group_list)
    result_traints = execute_query(query_traits.format(*personalitiy_avgs, user_group_str), [])
    return result_traints

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