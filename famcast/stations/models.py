import os
import re
import signal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import subprocess
import uuid
from rest_framework.exceptions import APIException
from django.db.models.signals import post_delete
from .helper import create_station_directory
from .icecast import create_icecast_config
from .nginx import create_nginx_config
from django.utils.text import slugify
from django.db.models.signals import pre_save

import logging

logger = logging.getLogger(__name__)


class Station(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    password = models.CharField(max_length=255)
    limit = models.IntegerField()
    mount = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255, default='localhost')
    port = models.IntegerField(unique=True, blank=True)
    station_key = models.CharField(max_length=255, unique=True, blank=True)
    icecast_pid = models.IntegerField(blank=True, null=True)

    def generate_slug(self):
        """
        Generate a unique slug for the station's name
        """
        original_slug = slugify(self.name)
        slug = original_slug
        suffix = 1

        # Check if a station with the same slug already exists
        while Station.objects.filter(slug=slug).exists():
            suffix += 1
            slug = f"{original_slug}-{suffix}"
        return slug

    def get_conf_dir(self):

        return f'/opt/stations/{self.slug}'

    def start_icecast(self):

        station_directory = os.path.join("/opt", "stations", self.slug)
        config_file_name = os.path.join(station_directory, "icecast.xml")
        process = subprocess.Popen(["icecast2", "-b", "-c", config_file_name])
        logger.info(f"Icecast process started with PID: {process.pid}")

        self.icecast_pid = process.pid
        self.save()
        self.refresh_from_db()
        logger.info(f"Icecast PID saved to database: {self.icecast_pid}")

    def stop_icecast(self):

        station_directory = os.path.join("/opt", "stations", self.slug)
        config_file_name = os.path.join(station_directory, "icecast.xml")
        subprocess.Popen(
            ["pkill", "-o", f"icecast2 -b -c {config_file_name}"],
        )

    def save(self, *args, **kwargs):
        if not self.id:
            # Generate a unique slug for the station's name
            self.slug = self.generate_slug()

            # Set default values for port and icecast_pid
            stations = Station.objects.order_by('port')

            if stations.exists():
                last_station = stations.last()
                self.port = last_station.port + 1
            else:
                self.port = 8003
            self.station_key = uuid.uuid4().hex
            if self.icecast_pid is None:  # only set to None when newly created
                self.icecast_pid = None
        super().save(*args, **kwargs)


@receiver(pre_save, sender=Station)
def station_pre_save(sender, instance, **kwargs):
    if instance.slug == '':
        instance.slug = instance.generate_slug()


@receiver(post_save, sender=Station)
def create_icecast2_create_nginx_config(sender, instance, created, **kwargs):
    if created:
        station_name = instance.slug
        # station_name = re.sub(r'[^a-z0-9-]', '', station_name)
        station_directory = create_station_directory(station_name)

        config_data = create_icecast_config(
            station_name, instance.port, instance.password, instance.limit, instance.mount, instance.hostname)

        config_file_name = os.path.join(station_directory, "icecast.xml")
        with open(config_file_name, "w") as f:
            f.write(config_data)
        # Start the Icecast2 instance
        process = subprocess.Popen(["icecast2", "-b", "-c", config_file_name])
        if process.returncode is not None:
            raise APIException(
                status_code=500, detail="Failed to start Icecast2 instance")
        # Generate the nginx configuration file
        nginx_config_data = create_nginx_config(
            station_name, instance.port, instance.mount)
        nginx_config_file_name = os.path.join(station_directory, "nginx.conf")
        with open(nginx_config_file_name, "w") as f:
            f.write(nginx_config_data)
        # Add firewall rule to allow traffic on the port
        subprocess.Popen(["sudo", "/usr/local/hestia/bin/v-add-firewall-rule",
                          "ACCEPT", "0.0.0.0/0", str(instance.port)])
        # Restart nginx to apply the new configuration
        subprocess.Popen(["sudo", "service", "nginx", "restart"])


@receiver(post_save, sender=Station)
@receiver(post_delete, sender=Station)
def update_nginx_conf(sender, **kwargs):
    stations = Station.objects.all()
    conf_file_path = '/home/admin/conf/web/nginx.ssl.conf_stations'

    with open(conf_file_path, 'w') as f:
        for station in stations:
            conf_file = os.path.join(station.get_conf_dir(), 'nginx.conf')
            f.write(f'    include {conf_file};\n')
     # reload nginx to apply the changes
    subprocess.Popen(["sudo", "service", "nginx", "restart"])


@receiver(post_save, sender=Station)
def update_icecast_config(sender, instance, **kwargs):
    # Update the Icecast configuration file
    station_name = instance.slug
    # station_name = re.sub(r'[^a-z0-9-]', '', station_name)
    station_directory = create_station_directory(station_name)
    config_file_name = os.path.join(station_directory, "icecast.xml")
    with open(config_file_name, "r") as f:
        config_data = f.read()
        config_data = re.sub(r"<password>.*?</password>",
                             f"<password>{instance.password}</password>", config_data)
        config_data = re.sub(r"<max-listeners>.*?</max-listeners>",
                             f"<max-listeners>{instance.limit}</max-listeners>", config_data)
        config_data = re.sub(r"<clients>.*?</clients>",
                             f"<clients>{instance.limit}</clients>", config_data)
    with open(config_file_name, "w") as f:
        f.write(config_data)

    # Restart Icecast to apply the new configuration

    process = subprocess.Popen(
        ["pkill", "-o", f"icecast2 -b -c {config_file_name}"],
    )
    if process.returncode is not None:
        raise Exception("Failed to stop Icecast2 instance")
    process = subprocess.Popen(["icecast2", "-b", "-c", config_file_name])
    if process.returncode is not None:
        raise Exception("Failed to start Icecast2 instance")


@receiver(post_delete, sender=Station)
def delete_station_files(sender, instance, **kwargs):
    station_name = instance.slug
    # station_name = re.sub(r'[^a-z0-9-]', '', station_name)
    station_directory = os.path.join("/opt/stations", station_name)
    icecast_config_file = os.path.join(
        station_directory, "icecast.xml")

    if os.path.exists(icecast_config_file):
        # Stop the Icecast instance
        process = subprocess.Popen(
            ["pkill", "-f", f"icecast2 -b -c {icecast_config_file}"])
        if process.returncode is not None:
            raise APIException(
                status_code=500, detail="Failed to stop Icecast2 instance")
        os.remove(icecast_config_file)

    nginx_config_file = os.path.join(station_directory, "nginx.conf")

    if os.path.exists(nginx_config_file):
        os.remove(nginx_config_file)
        # Restart nginx to apply the new configuration
        subprocess.Popen(["sudo", "service", "nginx", "restart"])
