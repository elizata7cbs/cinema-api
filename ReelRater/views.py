import logging
import requests
import time
from django.core.cache import cache
from rest_framework import generics
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .serializers import RecommendationsSerializer, RatingSerializer
from helpers import custom_response
logger = logging.getLogger('ReelRater')

class MovieListView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return the list of movies from the cache or external API
        cache_key = 'popular_movies'
        cached_movies = cache.get(cache_key)
        if cached_movies:
            return cached_movies

        url = f'{settings.TMDB_BASE_URL}movie/popular?api_key={settings.TMDB_API_KEY}&language=en-US&page=1'
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            movies = response.json().get('results', [])
            cache.set(cache_key, movies, timeout=3600)
            return movies
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching popular movies: {e}")
            raise

    def get(self, request, *args, **kwargs):
        start_time = time.perf_counter()
        movies = self.get_queryset()

        elapsed_time = time.perf_counter() - start_time
        logger.info(f"Fetched movies. Time taken: {elapsed_time:.6f} seconds.")

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(movies, request)
        return paginator.get_paginated_response(result_page)



class MovieDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, movie_id, *args, **kwargs):
        cache_key = f'movie_{movie_id}'
        start_time = time.perf_counter()

        cached_movie = cache.get(cache_key)
        if cached_movie:
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"Cache HIT for 'movie_{movie_id}'. Time to fetch from cache: {elapsed_time:.6f} seconds.")
            return custom_response(data=cached_movie, message="Movie fetched from cache successfully")

        url = f'{settings.TMDB_BASE_URL}movie/{movie_id}?api_key={settings.TMDB_API_KEY}&language=en-US'
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            movie = response.json()
            cache.set(cache_key, movie, timeout=3600)
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"Cache MISS for 'movie_{movie_id}'. Fetched from external API and cached. Time taken: {elapsed_time:.6f} seconds.")
            return custom_response(data=movie, message="Movie fetched successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching movie {movie_id}: {e}")
            return custom_response(errors=str(e), status=400, message="Error fetching movie")

class RecommendationsView(generics.CreateAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = RecommendationsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_preferences = serializer.validated_data
        url = f"{settings.TMDB_BASE_URL}discover/movie"
        params = {
            "with_genres": ",".join(user_preferences.get("genres", [])),
            "language": user_preferences.get("language", "en"),
            "primary_release_year": user_preferences.get("release_year"),
            "api_key": settings.TMDB_API_KEY,
        }
        try:
            response = requests.get(url, params=params, verify=False)
            response.raise_for_status()
            data = response.json()
            movie_details = [
                {
                    "title": movie.get("title"),
                    "description": movie.get("overview"),
                    "release_date": movie.get("release_date"),
                    "poster_path": movie.get("poster_path"),
                }
                for movie in data.get('results', [])
            ]
            logger.info("Fetched movie recommendations successfully.")
            return custom_response(data=movie_details, message="Recommendations fetched successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch recommendations: {e}")
            return custom_response(errors=str(e), status=400, message="Failed to fetch recommendations")

class RatingView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Movie rating saved successfully.")
        return custom_response(message="Rating saved successfully!", status=201)
