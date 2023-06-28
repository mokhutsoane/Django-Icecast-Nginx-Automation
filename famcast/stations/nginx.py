import re


def create_nginx_config(station_name: str, port: int, mount: str) -> str:
    #    # Convert the station name to lowercase and replace spaces with hyphens
    #     station_name = station_name.lower().replace(' ', '-')
    #     # Remove any remaining non-alphanumeric characters
    #     station_name = re.sub(r'[^a-z0-9-]', '', station_name)
    """Creates the nginx configuration file data for the given station name, port, and mount."""
    nginx_config_data = f"""
location /{station_name}/ {{
    proxy_set_header Accept-Encoding "";
    proxy_pass http://127.0.0.1:{port}/;
    sub_filter_types application/xspf+xml audio/x-mpegurl audio/x-vclt text/css text/html text/xml;
    sub_filter ':{port}/' '/';
    sub_filter 'localhost' $host;
    sub_filter 'Mount Point ' $host;
}}
    """
    return nginx_config_data
