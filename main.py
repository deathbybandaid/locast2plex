# pylama:ignore=E722,E303,E302,E305
import os
import sys
import time
from multiprocessing import Process
import platform

import LocastService
import SSDPServer
import L2Pconfig
from L2PTools import clean_exit
import HDHRInterface
import EPG2XML
import Facilities
import location_finder


if sys.version_info.major == 2 or sys.version_info < (3, 3):
    print('Error: Locast2Plex requires python 3.3+.')
    sys.exit(1)


# Startup Logic
if __name__ == '__main__':

    CURRENT_VERSION = "0.5.3"
    print("Initiating Locast2Plex v" + CURRENT_VERSION)

    # Get Operating system
    opersystem = platform.system()

    # set to directory of script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Open Configuration File
    print("Opening and Verifying Configuration File.")
    config = L2Pconfig.locast2plexConfig(script_dir)
    L2Pconfig.config_adjustments(config, opersystem, script_dir)

    print("Getting user location...")
    location_info = location_finder.LocastDMAFinder(config)

    locast = LocastService.LocastService(script_dir + "/", config, location_info.location)

    if (not locast.login(config.config["locast"]["username"], config.config["locast"]["password"])) or (not locast.validate_user()):
        print("Invalid Locast Login Credentials. Exiting...")
        clean_exit()

    station_list = locast.get_stations()
    print("Found " + str(len(station_list)) + " stations for DMA " + str(location_info.location["DMA"]))

    try:

        print("Starting Facilities thread...")
        Facilities.get_facilities(script_dir, config)
        epgServer = Process(target=Facilities.facilitesServerProcess, args=(script_dir + "/", config))
        epgServer.start()

        print("Starting device server on " + config.config["locast2plex"]['listen_address'] + ":" + config.config["locast2plex"]['listen_port'])
        HDHRInterface.hdhrinterface_start(config, locast, station_list, script_dir, location_info.location)

        print("Starting SSDP server...")
        ssdpServer = Process(target=SSDPServer.ssdpServerProcess, args=(config,))
        ssdpServer.daemon = True
        ssdpServer.start()

        print("Starting EPG thread...")
        epgServer = Process(target=EPG2XML.epgServerProcess, args=(script_dir + "/", config, location_info.location))
        epgServer.start()

        print("Locast2Plex is now online.")

        # wait forever
        while True:
            time.sleep(3600)

    except KeyboardInterrupt:
        print('^C received, shutting down the server')
        clean_exit()
