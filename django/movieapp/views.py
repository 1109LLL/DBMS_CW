# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import *
from .crawler import *
from .forms import MovieForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import connection
<<<<<<< HEAD
from django.core.paginator import Paginator
import math
=======
import logging

# Get an instance of a logger
logger = logging.getLogger('debug')
>>>>>>> eb42d5d87f6d17cfb3457be43069646c3b84823e

def get_genres_by_movieid(movieID):
    if movieID:
        query = '''select g.genreName from genres as g, moviesGenres as mg, movies as m 
        where g.genreID = mg.genreID and m.movieID = mg.movieID and m.movieID = %s'''
        with connection.cursor() as cursor:
            cursor.execute(query, [movieID])
            row = cursor.fetchall()
            genre_list = []
            for i in row:
                genre_list.append(i[0])
            return genre_list
    else:
        return []

def get_movieID_by_title(movieTitle):
    #find movieID based on movie title 
    query = '''select movieID from movies where movieTitle = %s'''
    with connection.cursor() as cursor:
        cursor.execute(query, [movieTitle.strip()])
        row = cursor.fetchall()
        return row # row[0][0]

def get_table_row_number(tableName):
    query = 'SELECT COUNT(*) FROM ' + tableName
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchall()
        return row 

def index(request):
    movie_search = request.GET.get('search')
    query = ''
    if movie_search:
        movieid = get_movieID_by_title(movie_search)
        genre_list = get_genres_by_movieid(movieid)
        query = "select movieID, movieTitle, movieAlias, MovieReleased from movies where movieTitle = %s"        
        with connection.cursor() as cursor:
            cursor.execute(query, [movie_search.strip()])
            row = cursor.fetchall()
            infors = zip(row, [genre_list])
            return render(request, 'movieapp/index.html', {'infors': infors})
    else:
        page = request.GET.get('page')
        query = 'SELECT movieID, movieTitle, movieAlias, MovieReleased FROM movies limit {}, 20'.format((int(page))*20 - 20)
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
            movie_number = math.ceil(get_table_row_number('movies')[0][0] / 20)
            return render(request, 'movieapp/index.html', {'infors': infors, 'cur_page':page, 'movie_number': movie_number})

def movie_panel(request):
    movie_selected = request.GET.get('select')
    movie_id = get_movie_id_by_title(movie_selected)
    if movie_selected and movie_id:
        # TODO add movie info logics
        # TODO can do in one search
        movie_title = movie_selected
        avg_rating = get_avg_rating_by_movie_id(movie_id)
        tags = get_tag_names_by_movie_id(movie_id)
        logger.debug(tags)
        imdb_id = get_imdb_link_by_movie_id(movie_id)
        url_img = get_imdb_img(imdb_id, movie_title)
        return render(request, 'movieapp/movie_panel.html', {'movie': movie_title, 'rating': avg_rating, 'tags': tags, 'img': url_img})
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
