from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User
import requests
from rest_framework import status


class RatingViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='liz', password='1234')
        response = self.client.post('/api/token/', {'username': 'liz', 'password': '1234'})
        self.token = response.data['access']

    def test_create_rating_success(self):
        # Define the data to send in the POST request
        rating_data = {
            "movie_id": 1,
            "rating": 4.5,
        }

        response = self.client.post(
            '/api/ratings/',
            data=rating_data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Check for success
        self.assertEqual(response.data["message"], "Rating saved successfully!")
        self.assertIn("status", response.data)



class MovieListViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='liz', password='1234')
        response = self.client.post('/api/token/', {'username': 'liz', 'password': '1234'})
        self.token = response.data['access']

    def test_fetch_movies_success(self):
        response = self.client.get(
            '/api/movies/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'  # Use the token for authentication
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)




class RecommendationsViewTest(TestCase):
    def setUp(self):
        # Create a test user and get the authentication token
        self.user = User.objects.create_user(username='liz', password='1234')
        response = self.client.post('/api/token/', {'username': 'liz', 'password': '1234'})
        self.token = response.data['access']
        self.url = reverse('movie-recommendations')

    @patch('requests.get')
    def test_create_recommendations_success(self, mock_get):
        # Mock successful API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [
                {"title": "Movie 1", "release_date": "2023-01-01"},
                {"title": "Movie 2", "release_date": "2023-02-01"}
            ]
        }

        response = self.client.post(
            self.url,
            {"language": "en", "release_year": 2023, "genres": ["Action"]},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'  # Include the token for authentication
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Expecting 200 OK
        self.assertEqual(len(response.data["data"]), 2)  # Expecting two movies
        self.assertEqual(response.data["data"][0]["release_date"], "2023-01-01")  # Verify release_date

    @patch('requests.get')
    def test_create_recommendations_failure(self, mock_get):
        # Mock the requests.get to raise an exception to simulate failure
        mock_get.side_effect = requests.exceptions.RequestException("API request failed")

        # Send valid data
        response = self.client.post(
            self.url,
            {"language": "en", "release_year": 2023, "genres": ["Action"]},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'  # Include the token for authentication
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["status"], 400)
        self.assertEqual(response.data["message"], "Failed to fetch recommendations")


class MovieDetailViewTest(TestCase):
    def setUp(self):
        # Create a test user and authenticate
        self.user = User.objects.create_user(username='liz', password='1234')
        response = self.client.post('/api/token/', {'username': 'liz', 'password': '1234'})
        self.token = response.data['access']
        self.movie_id = 20
        self.url = reverse('movie-detail', kwargs={'movie_id': self.movie_id})

    @patch('requests.get')
    def test_movie_detail_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": self.movie_id,
            "title": "Moana2",
            "release_date": "2023"
        }

        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], "Moana2")
        self.assertEqual(response.data["data"]["release_date"], "2023")
        self.assertIn("Movie fetched successfully", response.data["message"])