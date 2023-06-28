from rest_framework import serializers
from .models import Station


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'
      


class UpDateStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'
        extra_kwargs = {'name': {'required': False}, 'password': {
            'required': False}, 'mount': {'required': False}, 'limit': {'required': False}}