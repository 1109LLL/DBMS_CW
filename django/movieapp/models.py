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


def get_most_popular_movies(option):
    if option == "past_year":
        query = '''
                SELECT m.movieID, m.movieTitle, m.movieReleased, COUNT(m.movieID), ROUND(SUM(r.ratingFigure)/COUNT(m.movieID), 1) 
                FROM movies m JOIN ratings r ON m.movieID = r.movieID AND m.movieReleased = 2018
                GROUP BY m.movieID 
                ORDER BY COUNT(m.movieID) DESC
                limit 100
                '''
        return execute_query(query)
    else:
        option = 1
        query = '''
                SELECT m.movieID, m.movieTitle, m.movieReleased, COUNT(m.movieID), ROUND(SUM(r.ratingFigure)/COUNT(m.movieID), 1) 
                FROM movies m JOIN ratings r ON m.movieID = r.movieID
                GROUP BY m.movieID 
                ORDER BY COUNT(m.movieID) DESC
                limit 100
                '''
        return execute_query(query)

def get_average_rating_from_similar_tags(movie_id):
    tags = get_tag_names_by_movie_id(movie_id)
    if len(tags) == 0:
        return -1
    tags_list = []
    for t in tags:
        tags_list.append(t[0])
    tag_list = tuple(tags_list)

    query = '''  
            SELECT AVG(ratingFigure) FROM tags AS t
            INNER JOIN userTagsMovie AS utm ON t.tagID = utm.tagID AND t.tagName IN %s
            INNER JOIN ratings ON ratings.movieID = utm.movieID;
            '''
    result = execute_query(query, (tag_list,))
    return result[0][0]

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
        logger.info("img cache hit!")
        return img_url_cached if img_url_cached != "null" else ""
    logger.info("img cache miss!")
    # cache miss, crawl and write
    crawler = Crawler(movie_id, movie_title, LinkType.IMDB)
    # not available in imdb
    if not crawler:
        return ""
    img_url = crawler.get_imdb_img_url()
    # also cache if empty
    cache_value = img_url if img_url else "null"
    set_cache(cache, cache_key, cache_value, 60)
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
                 FROM ratings
                 WHERE movieID = %s AND ratingFigure <= 2) AS badRatings;
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

def get_avg_ratings_from_similar_genres(page):
    query = '''
            SELECT AVG(rg.ratingFigure)
            FROM (
            SELECT mg.genreID, AVG(r.ratingFigure) AS ratingFigure
            FROM ratings AS r, 
            moviesGenres AS mg
            WHERE r.movieID = mg.movieID
            AND r.movieID IN (SELECT m.movieID 
            FROM movies AS m 
            WHERE movieReleased = 0)
            GROUP BY mg.genreID) 
            AS rg,
            moviesGenres AS mg
            WHERE mg.genreID = rg.genreID
            AND mg.movieID IN (SELECT m.movieID 
            FROM movies AS m 
            WHERE movieReleased = 0)
            GROUP BY mg.movieID
            LIMIT {}, 20;
            '''.format((int(page))*20 - 20)
    result = execute_query(query)
    return result

def get_avg_rating_for_a_movie_from_similar_genres(movieID):
    query = '''
            SELECT AVG(rg.ratingFigure)
            FROM (
            SELECT mg.genreID AS genreID, AVG(r.ratingFigure) AS ratingFigure
            FROM ratings AS r, 
            moviesGenres AS mg
            WHERE r.movieID = mg.movieID
            AND r.movieID IN (SELECT m.movieID 
            FROM movies AS m 
            WHERE movieReleased = 0)
            GROUP BY mg.genreID) 
            AS rg
            WHERE rg.genreID IN
            (SELECT mg.genreID AS genreID 
            FROM moviesGenres AS mg 
            WHERE movieID = %s)
            ;
            '''
    result = execute_query(query,[movieID])
    return result[0][0]

def get_avg_ratings_from_seen_people(page):
    query = '''
            SELECT avg(r.ratingFigure) AS AverageRating 
            FROM ratings AS r 
            WHERE r.movieID IN 
            (SELECT m.movieID 
            FROM movies AS m 
            WHERE movieReleased = 0) 
            GROUP BY r.movieID
            LIMIT {}, 20;
            '''.format((int(page))*20 - 20)
    result = execute_query(query)
    avg_rating = []
    for i in result:
        avg_rating.append([i[0]])
    return avg_rating

def get_avg_rating_for_a_movie_from_seen_people(movieID):
    query = '''
            SELECT AVG(r.ratingFigure) 
            FROM ratings AS r 
            WHERE r.movieID = %s
            '''

    result = execute_query(query,[movieID])
    return result[0][0]

def get_genres_by_movieid(movie_id):
    if movie_id:
        query = '''
                SELECT g.genreName 
                FROM genres AS g, 
                moviesGenres AS mg, 
                movies AS m 
                WHERE g.genreID = mg.genreID 
                AND m.movieID = mg.movieID 
                AND m.movieID = %s;
                '''
        with connection.cursor() as cursor:
            cursor.execute(query, [movie_id])
            row = cursor.fetchall()
            genre_list = []
            for i in row:
                genre_list.append(i[0])
            return genre_list
    else:
        return []

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
            LIMIT %s, 5;
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

def get_index_movies_info(page):
    index = page
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

def get_personality_traits_by_user_group(user_group):
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
            WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.movieID = associated_user_movie_ID.movieID AND ratings.ratingFigure > 3
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
            WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.movieID = associated_user_movie_ID.movieID AND ratings.ratingFigure <= 3
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
                WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.ratingFigure > 3
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
                WHERE ratings.userID = associated_user_movie_ID.userID AND ratings.ratingFigure <= 3
                GROUP BY ratings.userID;
            '''
    haters_list = execute_query(haters, [tag])

    return likers_list, haters_list

def get_genre_user_groups(genre):
    likers ='''
            SELECT DISTINCT ratings.userID
            FROM 
                ratings,
                (SELECT movieID
                FROM 
                    moviesGenres,
                    (SELECT genreID
                    FROM genres
                    WHERE genreName = %s) AS select_genre
                WHERE select_genre.genreID = moviesGenres.genreID) as movie_with_genre
            WHERE movie_with_genre.movieID = ratings.movieID AND ratings.ratingFigure > 3;
            '''
    likers_list = execute_query(likers, [genre])

    haters ='''
            SELECT DISTINCT ratings.userID
            FROM 
                ratings,
                (SELECT movieID
                FROM 
                    moviesGenres,
                    (SELECT genreID
                    FROM genres
                    WHERE genreName = %s) AS select_genre
                WHERE select_genre.genreID = moviesGenres.genreID) as movie_with_genre
            WHERE movie_with_genre.movieID = ratings.movieID AND ratings.ratingFigure <= 3;
            '''
    haters_list = execute_query(haters, [genre])

    return likers_list, haters_list

def get_genre_lists_from_movieid(movieid):
    if not movieid:
        return None
    query = '''
            SELECT genreID
            FROM moviesGenres
            WHERE movieID = %s; 
            '''
    genres = execute_query(query, [movieid])
    genres_list = []
    for i in genres:
        genres_list.append(i[0])
    return genres_list

def get_movieid_by_genreid(genreid):
    if not genreid:
        return None
    query = '''
            SELECT movieID from moviesGenres
            WHERE genreID = %s;
            '''
    result = execute_query(query, [genreid])
    movieid_list = []
    for i in result:
        movieid_list.append(i[0])
    return movieid_list

def get_movie_list_containing_same_genres(genreid_lists): # [[0, 6, 4, 11, 12], [3, 6, 5]]
    movies_list = []
    for genreid_list in genreid_lists:
        temp_list = []
        for genreid in genreid_list:
            temp = get_movieid_by_genreid(genreid)
            if temp == None:
                continue
            else:
                temp_list = temp_list + temp
        movies_list.append(temp_list)
    return movies_list


def get_avg_ratings_of_lists_of_movies(movies_list):
    if not movies_list:
        return None
    splicing_movies_list = ""
    for i in movies_list:
        splicing_movies_list = splicing_movies_list + str(i) + ','
    splicing_movies_list = splicing_movies_list.strip(",") 
    query = '''
            SELECT AVG(ratingFigure)
            FROM ratings
            WHERE movieID in (%s);
            '''
    result = execute_query(query, [splicing_movies_list])
    avg_rating = []
    for i in result:
        avg_rating.append(i[0])
    return avg_rating
    
def get_personality_traits_by_movie_id(movie_id):
    traits_cache = get_cache_personality_traits(movie_id)
    if traits_cache:
        # cache hit
        logger.info("traits cache hit!")
        return traits_cache
    # cache miss
    logger.info("traits cache miss!")
    user_group = get_personality_user_group_by_movie_id(movie_id)
    traits = get_personality_traits_by_user_group(user_group)
    if traits and traits[0]:
        set_cache_personality_traits(movie_id, traits[0])
    return traits[0]

def get_cache_personality_traits(movie_id):
    key_trait_base = str(movie_id) + "_personality_traits_{0}"
    traits_cache = []
    for i in range(5):
        key_trait = key_trait_base.format(i)
        trait_cache = get_cache(cache, key_trait)
        if not trait_cache:
            return None
        traits_cache.append(trait_cache)
    return traits_cache

def set_cache_personality_traits(movie_id, traits):
    key_trait_base = str(movie_id) + "_personality_traits_{0}"
    for i in range(5):
        set_cache(cache, key=key_trait_base.format(i), value=traits[i], ttl=60)