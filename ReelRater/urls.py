from django.urls import path
from .views import MovieListView, MovieDetailView, RecommendationsView, RatingView

urlpatterns = [

    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('movie/<int:movie_id>/', MovieDetailView.as_view(), name='movie-detail'),
    path('recommendations/', RecommendationsView.as_view(), name='movie-recommendations'),
    path('ratings/', RatingView.as_view(), name='save_rating'),

]
