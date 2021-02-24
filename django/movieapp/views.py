# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import *
from .crawler import *
from .forms import MovieForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import connection
import logging

# Get an instance of a logger
logger = logging.getLogger('debug')

def index(request):
    movie_search = request.GET.get('search')
    query = ''
    if movie_search:
        query = 'SELECT * FROM movies WHERE movieTitle = %s '
        with connection.cursor() as cursor:
            cursor.execute(query, [movie_search])
            row = cursor.fetchall()
            return render(request, 'movieapp/index.html', {'movies': row})
    else:
        query = 'SELECT * FROM movies'
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchall()
            return render(request, 'movieapp/index.html', {'movies': row})

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
