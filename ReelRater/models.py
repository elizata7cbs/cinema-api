from django.db import models


class Rating(models.Model):
    movie_id = models.IntegerField()
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
