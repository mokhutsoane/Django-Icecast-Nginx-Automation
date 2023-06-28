
def create_icecast_config(station_name: str, port: int, password: str, limit: int, mount: str, hostname: str = "famcast.co.za") -> str:
    """Creates the Icecast2 configuration file data for the given port, password, limit, mount, and hostname."""
    config_data = f"""    
    <icecast>

    <location>South Africa</location>
    <admin>info@{hostname}</admin>

    <hostname>{hostname}</hostname>

    <limits>
       
        <clients>{limit}</clients>
        <sources>2</sources>
        <queue-size>524288</queue-size>
        <client-timeout>30</client-timeout>
        <header-timeout>15</header-timeout>
        <source-timeout>10</source-timeout>
       
        <burst-size>65535</burst-size>
    </limits>

    <authentication>
        <source-password>{password}</source-password>
        <relay-password>{password}</relay-password>
        <admin-user>admin</admin-user>
        <admin-password>{password}</admin-password>
    </authentication>

  
    <listen-socket>
        <port>{port}</port>
     
    </listen-socket>
   

    <http-headers>
        <header type="cors" name="Access-Control-Allow-Origin" />
        <header type="cors" name="Access-Control-Allow-Headers" />
        <header type="cors" name="Access-Control-Expose-Headers" />
    </http-headers>
    
    <mount type="normal">
        <mount-name>/{mount}</mount-name>
        <max-listeners>{limit}</max-listeners>
        <dump-file>/tmp/dump-example1.ogg</dump-file>
        <burst-size>65536</burst-size>
        <fallback-mount>/example2.ogg</fallback-mount>
        <fallback-override>true</fallback-override>
        <fallback-when-full>true</fallback-when-full>
        <intro>/example_intro.ogg</intro>
        <public>true</public>   
    </mount>   

      <fileserve>1</fileserve>

    <paths>
        <!-- basedir is only used if chroot is enabled -->
        <basedir>/usr/share/icecast2</basedir>

        <!-- Note that if <chroot> is turned on below, these paths must both
             be relative to the new root, not the original root -->
        <logdir>/var/log/icecast2</logdir>
        <accesslog>{station_name}-access.log</accesslog>
        <webroot>/usr/share/icecast2/web</webroot>
        <adminroot>/usr/share/icecast2/admin</adminroot>
        <!-- <pidfile>/usr/share/icecast2/icecast.pid</pidfile> -->

        <!-- Aliases: treat requests for 'source' path as being for 'dest' path
             May be made specific to a port or bound address using the "port"
             and "bind-address" attributes.
          -->
        <!--
        <alias source="/foo" destination="/bar"/>
        -->
        <!-- Aliases: can also be used for simple redirections as well,
             this example will redirect all requests for http://server:port/ to
             the status page
        -->
        <alias source="/" destination="/status.xsl"/>
        <!-- The certificate file needs to contain both public and private part.
             Both should be PEM encoded.
        <ssl-certificate>/usr/share/icecast2/icecast.pem</ssl-certificate>
        -->
    </paths>
</icecast>
    """
    return config_data
