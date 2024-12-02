from rest_framework import serializers
from .models import  Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["movie_id", "rating"]




class RecommendationsSerializer(serializers.Serializer):
    genres = serializers.ListField(child=serializers.CharField(), required=False)
    language = serializers.CharField(required=False, default="en")
    release_year = serializers.IntegerField(required=False)
