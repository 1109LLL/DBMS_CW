"""movieProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('popular/', views.most_popular, name='popular'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie_panel', views.movie_panel, name='movie_panel'),
    path('predicted_movie_panel', views.predicted_movie_panel, name='predicted_movie_panel'),
    path('polarising', views.polarising, name='polarising'),
    path('movies/edit/<int:pk>/', views.edit, name='edit'),
    path('soon_released_prediction', views.soon_to_be_released_movie_prediction, name='soon_released_prediction'),
    path('user_segmentation_by_ratings', views.user_segmentation_by_ratings, name='user_segmentation_by_ratings'),
    path('user_segmentation_by_genres', views.user_segmentation_by_genres, name='user_segmentation_by_genres')
]
