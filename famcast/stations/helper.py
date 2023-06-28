import os


def create_station_directory(station_name: str) -> str:
    """Creates a directory for the station with the given name in the /opt directory and returns the path to the directory."""
    station_directory = os.path.join("/opt", "stations", station_name)
    os.makedirs(station_directory, exist_ok=True)
    return station_directory
