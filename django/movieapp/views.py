# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import Movie
from .forms import MovieForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import connection


def index(request):
    movie_search = request.GET.get('search')
    query = ''
    if movie_search:
        query = 'SELECT * FROM movies WHERE movieTitle = %s'
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
