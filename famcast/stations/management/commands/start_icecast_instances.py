import os
import re
from django.core.management.base import BaseCommand
import subprocess

from stations.models import Station

class Command(BaseCommand):
    help = 'Starts all Icecast instances'

    def handle(self, *args, **options):
        stations = Station.objects.all()
        for station in stations:
            radio_name = station.name.lower().replace('','-')
            # Convert the station name to lowercase and replace spaces with hyphens
            station_name = station.name.lower().replace(' ', '-')
            # Remove any remaining non-alphanumeric characters
            radio_name = re.sub(r'[^a-z0-9-]', '', station_name)
            station_directory = os.path.join("/opt", "stations", radio_name)
            config_file_name = os.path.join(station_directory, "icecast.xml")
            process = subprocess.Popen(["icecast2","-b","-c", config_file_name])
            if process.returncode is not None:
                self.stdout.write(self.style.ERROR(f"Failed to start Icecast2 instance for {station.name}-{station.port}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Successfully started Icecast2 instance for {station.name}-{station.port}"))
