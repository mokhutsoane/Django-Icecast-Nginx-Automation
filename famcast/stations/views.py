import os
import re
import subprocess
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Station
from .serializers import StationSerializer, UpDateStationSerializer
from django.http import HttpResponseForbidden
from django.conf import settings
import psutil
import socket


def is_icecast_running(station):
    if station.icecast_pid is None:
        return False
    try:
        process = psutil.Process(station.icecast_pid)
        return process.name() == "icecast2"
    except psutil.NoSuchProcess:
        return False


def check_icecast_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def api_key_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key != settings.API_KEY:
            return HttpResponseForbidden('Invalid API key')
        return view_func(request, *args, **kwargs)

    return wrapped_view


def trusted_origin_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        trusted_origin = 'https://www.example.com/'
        if request.META.get('HTTP_REFERER') != trusted_origin:
            return Response({'error': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)

    return wrapped_view


@api_view(['POST'])
@api_key_required
# @trusted_origin_required
def create_station(request):
    serializer = StationSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@api_key_required
# @trusted_origin_required
def update_station(request, station_id):
    try:
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

    station_key = request.query_params.get(
        'station_key') or request.data.get('station_key')
    if station_key != station.station_key:
        return Response({'error': 'Invalid Station key'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = UpDateStationSerializer(instance=station, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@api_key_required
# @trusted_origin_required
def delete_station(request, station_id):

    try:
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
    # station_key = request.query_params.get(
    #     'station_key') or request.data.get('station_key', None)
    station_key = request.query_params.get(
        'station_key', None) or request.data.get('station_key', None)

    if station_key != station.station_key:
        return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)

    station.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@api_key_required
# @trusted_origin_required
def get_station(request, station_id):
    try:
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
    station_key = request.query_params.get(
        'station_key') or request.data.get('station_key')

    if station_key != station.station_key:
        return Response({'error': 'Invalid Station key'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = StationSerializer(station)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@api_key_required
def check_station(request, station_id):
    try:
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

    station_key = request.query_params.get(
        'station_key') or request.data.get('station_key')

    if station_key != station.station_key:
        return Response({'error': 'Invalid Station key'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if Icecast is running
    if check_icecast_port(station.port):
        return Response('Icecast is running', status=200)

    return Response('Icecast is stopped', status=200)


@api_view(['POST'])
@api_key_required
def start_station(request, station_id):
    try:
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

    station_key = request.query_params.get(
        'station_key') or request.data.get('station_key')

    if station_key != station.station_key:
        return Response({'error': 'Invalid Station key'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if Icecast is already running
    if check_icecast_port(station.port):
        return Response('Icecast is already running', status=200)

    # Start Icecast
    station.start_icecast()

    return Response('Starting Icecast...', status=200)
