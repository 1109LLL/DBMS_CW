# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import *
from .crawler import *
from .helpers import *
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import connection
from django.core.paginator import Paginator
import math
import logging

# Get an instance of a logger
logger = logging.getLogger('debug')

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

def index(request):
    movie_search = request.GET.get('search')
    page = request.GET.get('page')
    page = int(page) if page and int(page) > 0 else 1
    # either show all or show search results
    movies_info = get_search_movies_info(movie_search, page) if movie_search else get_index_movies_info(page)
    # genres csv to list
    movies_info = fix_movies_info_genres(movies_info, genres_index=4)
    movie_num = total_number_of_movies()
    page_num = get_page_num(movie_num)

    context = {
        'movies_info': movies_info, 
        'cur_page':page, 
        'page_num': page_num
    }

    return render(request, 'movieapp/index.html', context)

def movie_panel(request):
    movie_selected = request.GET.get('select')
    has_traits = True if request.GET.get('traits') else False
    movie_id = get_movie_id_by_title(movie_selected)
    if movie_selected and movie_id:
        # TODO add movie info logics
        # TODO can do in one search

        movie_title = movie_selected
        released_year = get_released_year_by_movie_id(movie_id)
        avg_rating = get_avg_rating_by_movie_id(movie_id)
        # round the rating to 2s.f.
        avg_rating = round(float(avg_rating), 1) if avg_rating else avg_rating
        tags = get_tag_names_by_movie_id(movie_id)
        genres = get_genres_by_movieid(movie_id)
        link_ids = get_link_ids_by_movie_id(movie_id)
        imdb_id = link_ids[0]
        tmdb_id = link_ids[1] 
        url_img = get_imdb_img(imdb_id, movie_title)

        context = {
            'movie': movie_title, 
            'year': released_year, 
            'rating': avg_rating, 
            'tags': tags,
            'genres': genres, 
            'img': url_img, 
            'imdb_id': imdb_id, 
            'tmdb_id': tmdb_id
        }

        # predict personality trait
        if has_traits:
            user_group = get_personality_user_group_by_movie_id(movie_id)
            traits = get_personality_traits(user_group)
            traits = [round(trait, 2) for trait in traits[0]] if traits else []
            personality_traits = list(zip(personalities, traits))
            context['traits'] = personality_traits
            
        return render(request, 'movieapp/movie_panel.html', context)
    else:
        return redirect('index')

def predicted_movie_panel(request):
    movie_selected = request.GET.get('select')
    movie_id = get_movie_id_by_title(movie_selected)
    
    if movie_selected and movie_id:
        avg_rating1 = get_avg_rating_for_a_movie_from_seen_people(movie_id)
        avg_rating2 = get_avg_rating_for_a_movie_from_similar_genres(movie_id)
        avg_rating3 = get_average_rating_from_similar_tags(movie_id)

        # Check if tags exist
        if avg_rating3 == -1:
            avg_rating = (avg_rating1+avg_rating2) / 2
        else:
            avg_rating = (avg_rating1+avg_rating2+avg_rating3) / 3
        # round the rating to 2s.f.
        avg_rating = round(float(avg_rating), 1) if avg_rating else avg_rating

        movie_title = movie_selected
        released_year = get_released_year_by_movie_id(movie_id)
        tags = get_tag_names_by_movie_id(movie_id)
        genres = get_genres_by_movieid(movie_id)
        link_ids = get_link_ids_by_movie_id(movie_id)
        imdb_id = link_ids[0]
        tmdb_id = link_ids[1] 
        url_img = get_imdb_img(imdb_id, movie_title)

        return render(request, 'movieapp/predicted_movie_panel.html', {'movie': movie_title, 'year': released_year, 'rating': avg_rating, 'tags': tags,
                                                             'genres': genres, 'img': url_img, 'imdb_id': imdb_id, 'tmdb_id': tmdb_id})
    else:
        return redirect('index')


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
    result = execute_query(query, (tags_list,))
    return result[0][0]



def most_popular(request):
    year = request.GET.get('option')
    row = []
    option = 1
    if year == "":
        query = '''
                SELECT m.movieID, m.movieTitle, m.movieReleased, COUNT(m.movieID), ROUND(SUM(r.ratingFigure)/COUNT(m.movieID), 1) 
                FROM movies m JOIN ratings r ON m.movieID = r.movieID AND m.movieReleased = 2018
                GROUP BY m.movieID 
                ORDER BY COUNT(m.movieID) DESC
                limit 100
                '''
        option = 2
        row = execute_query(query)
    else:
        option = 1
        query = '''
                SELECT m.movieID, m.movieTitle, m.movieReleased, COUNT(m.movieID), ROUND(SUM(r.ratingFigure)/COUNT(m.movieID), 1) 
                FROM movies m JOIN ratings r ON m.movieID = r.movieID
                GROUP BY m.movieID 
                ORDER BY COUNT(m.movieID) DESC
                limit 100
                '''
        row = execute_query(query)
    return render(request, 'movieapp/popular.html', {'movies': row, 'option': option})

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

def soon_to_be_released_movie_prediction(request):
    page = request.GET.get('page')
    classification = request.GET.get('option')
    page = page if page else 1
    query = '''
            SELECT movieID, movieTitle, movieAlias, movieReleased 
            FROM movies
            WHERE movieReleased = 0
            LIMIT {}, 20;
            '''.format((int(page))*20 - 20)
    result = execute_query(query)
    
    avg_rating_list_by_seen_people = get_avg_ratings_from_seen_people(page) # people who have seen avg rating
    avg_rating_list_by_genres = get_avg_ratings_from_similar_genres(page)
    avg_rating_list_by_tags = []

    for movie in result:
        avg_rating_list_by_tags.append(get_average_rating_from_similar_tags(movie[0]))

    avg_rating_from_3_factors = []
    option = 0
    if classification == 'People':
        option = 1
        avg_rating_from_3_factors = [[round(float(x[0]), 1) if x else x] for x in avg_rating_list_by_seen_people]

    elif classification == 'Genres':
        option = 2
        avg_rating_from_3_factors = [[round(float(x[0]), 1) if x else x] for x in avg_rating_list_by_genres]

    elif classification == 'Tags':
        option = 3
        avg_rating_from_3_factors = [[round(float(x), 1) if x else x] for x in avg_rating_list_by_tags]

    else:
        option = 0
        for i in range(0, len(avg_rating_list_by_seen_people)):
            if avg_rating_list_by_tags[i] != -1:
                temp_rating = (avg_rating_list_by_seen_people[i][0] + avg_rating_list_by_genres[i][0] + avg_rating_list_by_tags[i]) / 3
            else:
                temp_rating = (avg_rating_list_by_seen_people[i][0] + avg_rating_list_by_genres[i][0]) / 2
            temp_rating = round(float(temp_rating), 1) if temp_rating else temp_rating
            avg_rating_from_3_factors.append([temp_rating])
    
    logger.info(classification)

    infors = zip(result, avg_rating_from_3_factors)

    total_pages = get_prediction_movies_row_number()
    page_number = math.ceil(total_pages / 20)
    return render(request, 'movieapp/soon_released_prediction.html', {'soon_to_be_released':result, 'cur_page':page, 'page_number': page_number, 'infors':infors, 'option':option})

def polarising(request):
    pointer = request.GET.get('pointer')
    if pointer is None:
        pointer = 0
    else:
        pointer = int(pointer)
    movie_id_list = get_movie_id_list()

    polarizing_movies = []
    i = pointer
    for movie_id in movie_id_list[pointer:]:
        i += 1
        polarized, good_ratio, bad_ratio, good_rating_count, bad_rating_count = determine_polarization(movie_id[0])

        info = []
        # info :: [movie_name, movie_id, good_ratings%, bad_ratings%, genres, tags]
        if polarized:
            info.append(get_movie_name_by_movie_id(movie_id)[0][0])
            info.append(movie_id[0])
            info.append(good_ratio)
            info.append(bad_ratio)
            info.append(get_genres_by_movieid(movie_id))
            info.append(get_tag_names_by_movie_id(movie_id))
            info.append(good_rating_count)
            info.append(bad_rating_count)
            polarizing_movies.append(info)
        
        if len(polarizing_movies) == 20:
            return render(request, 'movieapp/polarising.html', {'polarizing_movies':polarizing_movies, 'list_pointer':i})

    return render(request, 'movieapp/polarising.html', {'polarizing_movies':polarizing_movies, 'list_pointer':i})

def user_segmentation_by_ratings(request):
    page = request.GET.get('page')
    page = page if page else 1
    limit = (int(page))*20 - 20
    movie_id_list = get_limited_movies(limit)

    segmented = []
    tags = []
    #  tags = [movie1[zip(tag_names|users(likers,haters|general_users_list))]]

    for movie_id in movie_id_list:
        info = []
        counts, likers, haters = gather_user_groups(movie_id[0])
        info.append(get_movie_name_by_movie_id(movie_id)[0][0])
        info.append(counts[0][0])
        info.append(counts[0][1])
        info.append(likers)
        info.append(haters)
        
        tag_names = get_tag_names_by_movie_id(movie_id)
        users_list = []
        general_users_list = []
        for tag in tag_names:
            curr_tag = tag[0]
            likers, haters = preference_by_tag(curr_tag)
            users_list.append(likers)
            users_list.append(haters)

            likers_general, haters_general = general_preference_by_tag(curr_tag)
            general_users_list.append(likers_general)
            general_users_list.append(haters_general)

        tags.append(list(zip(tag_names, users_list, general_users_list)))
        segmented.append(info)

    doc = list(zip(segmented, tags))

    total_pages = total_number_of_movies()
    movie_number = math.ceil(total_pages / 20)
    return render(request, 'movieapp/user_segmentation.html', {'segments':doc, 'cur_page':page, 'movie_number':movie_number})


def predict_personality_traits(request):
    movies_info = get_personality_qualified_movies()
    movies_info = fix_movies_info_genres(movies_info, genres_index=4)
    page_num = get_page_num(len(movies_info))

    context = {
        'movies_info': movies_info, 
        'cur_page': 1, 
        'page_num': page_num, 
        'page_title': "Predict Personality Traits"
    }

    return render(request, 'movieapp/predict_personality_traits.html', context)
    
