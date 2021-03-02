# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import *
from .crawler import *
from .forms import MovieForm
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
                SELECT g.genreName FROM genres AS g, moviesGenres AS mg, movies AS m 
                WHERE g.genreID = mg.genreID AND m.movieID = mg.movieID AND m.movieID = %s;
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
    query = ''
    if movie_search:
        movie_id = get_movieID_by_title(movie_search)
        genre_list = get_genres_by_movieid(movie_id)
        query = """
                SELECT movieID, movieTitle, movieAlias, MovieReleased 
                FROM movies 
                WHERE movieTitle = %s
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [movie_search.strip()])
            row = cursor.fetchall()
            infors = zip(row, [genre_list])
            return render(request, 'movieapp/index.html', {'infors': infors})
    else:
        page = request.GET.get('page')
        page = page if page else 1
        query = '''
                SELECT movieID, movieTitle, movieAlias, MovieReleased 
                FROM movies limit {}, 20;
                '''.format((int(page))*20 - 20)
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchall()
            movieID_list = []
            for i in row:
                movieID_list.append(i[0])
            full_genres_list = []
            for id in movieID_list:
                full_genres_list.append(get_genres_by_movieid(id))
            infors = zip(row, full_genres_list) 
            total_pages = get_table_row_number('movies')[0][0] 
            movie_number = math.ceil(total_pages / 20)
            return render(request, 'movieapp/index.html', {'infors': infors, 'cur_page':page, 'movie_number': movie_number})

def movie_panel(request):
    movie_selected = request.GET.get('select')
    movie_id = get_movie_id_by_title(movie_selected)
    if movie_selected and movie_id:
        # TODO add movie info logics
        # TODO can do in one search
        movie_title = movie_selected
        released_year = get_released_year_by_movie_id(movie_id)
        avg_rating = get_avg_rating_by_movie_id(movie_id)
        avg_rating = round(float(avg_rating), 1) if avg_rating else avg_rating
        tags = get_tag_names_by_movie_id(movie_id)
        genres = get_genres_by_movieid(movie_id)
        imdb_id = get_imdb_link_by_movie_id(movie_id)
        url_img = get_imdb_img(imdb_id, movie_title)
        return render(request, 'movieapp/movie_panel.html', {'movie': movie_title, 'year': released_year, 'rating': avg_rating, 'tags': tags, 'genres': genres, 'img': url_img})
    else:
        return redirect('index')

def movie_edit(request):
    search = request.GET.get('search')
    query = ''
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchall()
        return render(request, 'movieapp/index.html', {'movies': row})


def create(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    form = MovieForm()

    return render(request,'movieapp/create.html',{'form': form})

def edit(request, pk, template_name='movieapp/edit.html'):
    Movie = get_object_or_404(Movie, pk=pk)
    form = MovieForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('index')
    return render(request, template_name, {'form':form})

def soon_to_be_released_movie_prediction(request):
    # if request.method == 'GET':
    page = request.GET.get('page')
    page = page if page else 1
    query = '''
            SELECT movieID, movieTitle, movieAlias, movieReleased 
            FROM movies
            WHERE movieReleased = 0
            LIMIT {}, 20;
            '''.format((int(page))*20 - 20)
    result = execute_query(query)
    avg_rating_list = []
    for movie_search in result:
        movie_search = movie_search[1]
        movie_id = get_movieID_by_title(movie_search)
        # TODO can select parts of user as 先看过的人
        avg_rating = get_avg_rating_by_movie_id(movie_id[0][0])
        avg_rating = round(float(avg_rating), 1) if avg_rating else avg_rating
        avg_rating_list.append([avg_rating])
    infors = zip(result, avg_rating_list)
    # logger.info(avg_rating_list)
    # logger.info(result)


    total_pages = 252 ## need change...
    movie_number = math.ceil(total_pages / 20)
    return render(request, 'movieapp/soon_released_prediction.html', {'soon_to_be_released':result, 'cur_page':page, 'movie_number': movie_number, 'infors':infors})    

def polarising(request):
    if request.method == 'GET':
        movie_id_list = get_movie_id_list()

        polarizing_movies = []
        for movie_id in movie_id_list:
            ratings = get_ratings_by_movie_id(movie_id)
            polarized, good_ratio, bad_ratio = determine_polarizition(ratings)

            info = []
            # info :: [movie_name, movie_id, good_ratings%, bad_ratings%, genres, tags]
            if polarized:
                info.append(get_movie_name_by_movie_id(movie_id)[0][0])
                info.append(movie_id[0])
                info.append(good_ratio)
                info.append(bad_ratio)
                info.append(get_genres_by_movieid(movie_id))
                info.append(get_tag_names_by_movie_id(movie_id))

                polarizing_movies.append(info)

        return render(request, 'movieapp/polarising.html', {'polarizing_movies':polarizing_movies})
