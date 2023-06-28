from . import views
from django.urls import path


urlpatterns = [
    # path('stations2/', StationList.as_view(), name='create-station2'),
    path('stations/', views.create_station, name='create-station'),
    path('stations/<int:station_id>/update',
         views.update_station, name='update_station'),

    path('stations/<int:station_id>/delete/', views.delete_station),

    path('stations/<int:station_id>/check/', views.check_station),

    path('stations/<int:station_id>/get/',
         views.get_station, name='single_station'),

    path('stations/<int:station_id>/start/',
         views.start_station, name='start_station'),




    # path('stations-list/', views.list_stations, name='list-station'),


]
