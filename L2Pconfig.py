import os
import random
import configparser
from pathlib import Path

from L2PTools import is_docker, clean_exit


class locast2plexConfig():

    config_file = None
    config_handler = configparser.ConfigParser()

    config = {
                "main": {
                        'uuid': None,
                        },
                "locast2plex": {
                                "listen_address": "0.0.0.0",
                                "listen_port": "6077",
                                'tuner_count': '3',
                                'concurrent_listeners': '10',  # to convert
                                },
                "locast": {
                            "username": None,
                            "password": None,
                            },
                "dev": {
                        'override_latitude': None,
                        'override_longitude': None,
                        'mock_location': None,
                        'override_zipcode': None,
                        'bytes_per_read': '1152000',
                        'reporting_model': 'HDHR3-US',
                        'reporting_firmware_name': 'hdhomerun3_atsc',
                        'reporting_firmware_ver': '20150826',
                        'epg_delay': 43200,
                        'ffmpeg_path': None,
                        }
    }

    def __init__(self, script_dir):
        self.get_config_path(script_dir)
        self.import_config()

    def get_config_path(self, script_dir):
        for x in ['/config/config.ini', '/config.ini']:
            if os.path.exists(script_dir + x):
                self.config_file = Path(script_dir + x)
                break
        if not self.config_file:
            print("Config file missing, Exiting...")
            clean_exit()

    def import_config(self):
        self.config_handler.read(self.config_file)
        for each_section in self.config_handler.sections():
            for (each_key, each_val) in self.config_handler.items(each_section):
                self.config[each_section.lower()][each_key.lower()] = each_val

    def write(self, section, key, value):
        self.config[section][key] = value
        self.config_handler.set(section, key, value)

        with open(self.config_file, 'w'):
            self.config_handler.write(self.config_file)


def config_adjustments(config, opersystem, script_dir):

    if not config.config["locast"]["username"] or not config.config["locast"]["password"]:
        print("Locast Login Credentials Missing. Exiting...")
        clean_exit()

    # Tuner Count Cannot be greater than 3
    try:
        TUNER_COUNT = int(config.config["locast2plex"]["tuner_count"])
        if not 1 <= TUNER_COUNT <= 4:
            print("Tuner count set outside of 1-4 range.  Setting to default")
            config.config["locast2plex"]["tuner_count"] = 3
    except ValueError:
        print("tuner_count value is not valid.  Setting to default")
        config.config["locast2plex"]["tuner_count"] = 3
    print("Tuner count set to " + str(config.config["locast2plex"]["tuner_count"]))

    # docker users only configure the outside port, but for those running in command line/terminal
    # these will be the same
    if not is_docker():
        config.config["locast2plex"]["listen_address"] = config.config["locast2plex"]["listen_address"]
        config.config["locast2plex"]["listen_port"] = config.config["locast2plex"]["listen_port"]
    print("Server is set to run on  " +
          str(config.config["locast2plex"]["listen_address"]) + ":" +
          str(config.config["locast2plex"]["listen_port"]))

    # generate UUID here for when we are not using docker
    if config.config["main"]["uuid"] is None:
        print("No UUID found.  Generating one now...")
        # from https://pynative.com/python-generate-random-string/
        # create a string that wouldn't be a real device uuid for
        config.config["main"]["uuid"] = ''.join(random.choice("hijklmnopqrstuvwxyz") for i in range(8))
        config.write('main', 'uuid', config.config["main"]["uuid"])
    print("UUID set to: " + config.config["main"]["uuid"] + "...")

    if (config.config["dev"]["override_latitude"] is not None) and (config.config["dev"]["override_longitude"] is not None):
        config.config["dev"]["mock_location"] = {
            "latitude": config.config["main"]["dev"],
            "longitude": config.config["main"]["dev"]
        }

    if not config.config["dev"]["ffmpeg_path"]:
        if opersystem in ["Windows"]:
            config.config["dev"]["ffmpeg_path"] = script_dir + "/ffmpeg/ffmpeg.exe"
        else:
            config.config["dev"]["ffmpeg_path"] = "ffmpeg"
