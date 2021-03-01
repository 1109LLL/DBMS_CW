# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import Movie
from .forms import MovieForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import connection

def get_genres_by_movieid(movieID):
    query = '''select g.genreName from genres as g, moviesGenres as mg, movies as m 
    where g.genreID = mg.genreID and m.movieID = mg.movieID and m.movieID = %s'''
    with connection.cursor() as cursor:
        cursor.execute(query, [movieID])
        row = cursor.fetchall()
        genre_list = []
        for i in row:
            genre_list.append(i[0])
        return genre_list

def get_movieID_by_title(movieTitle):
    #find movieID based on movie title 
    query = '''select movieID from movies where movieTitle = %s'''
    with connection.cursor() as cursor:
        cursor.execute(query, [movieTitle])
        row = cursor.fetchall()
        return row # row[0][0]
        
def index(request):
    movie_search = request.GET.get('search')
    query = ''
    if movie_search:
        movieid = get_movieID_by_title(movie_search)
        genre_list = get_genres_by_movieid(movieid)
        query = "select movieID, movieTitle, MovieReleased from movies where movieTitle = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [movie_search.strip()])
            row = cursor.fetchall()
            infors = zip(row, [genre_list])
            return render(request, 'movieapp/index.html', {'infors': infors})
    else:
        query = 'SELECT movieID, movieTitle, MovieReleased FROM movies limit 100'
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
            return render(request, 'movieapp/index.html', {'infors': infors})

def most_popular(request):
    query = "SELECT m.movieID, m.movieTitle, m.movieReleased, ROUND(SUM(r.ratingFigure)/COUNT(m.movieID), 1) FROM movies m JOIN ratings r ON m.movieID = r.movieID GROUP BY m.movieID ORDER BY COUNT(m.movieID), m.movieReleased DESC limit 50"
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchall()
        return render(request, 'movieapp/popular.html', {'movies': row})

def movie_detail(request, movie_id):
    #page = (int)(request.GET.get('page'))
    query = "select movieID, movieTitle, MovieReleased from movies where movieID = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, movie_id)
        row = cursor.fetchall()
        return render(request, 'movieapp/movie.html', {'movies': row, 'page': 1})


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
