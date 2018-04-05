#!/usr/local/bin/python3.5

from time import sleep
from multiprocessing import Lock
import logging

import pychromecast
import os
import bot

POLL_INTERVAL = 1800

class ChromecastListener(object):
    def __init__(self, player, bot):
        self._song = None
        self._player = player
        self._bot = bot
        self._lock = Lock()
        
    def get_source(self, status):
        if "soundcloud" in status.content_id:
            return "SoundCloud"
        if "youtube" in status.content_type:
            return "YouTube"
        if "spotify" in status.content_type:
            return "Spotify"
        else:
            logging.debug("Unknown source: content_id=%s, content_type=%s" % (status.content_id, status.content_type))
        return os.environ.get('USERNAME', 'Discobear')

    def new_media_status(self, status):
        logging.debug("[%s] Got new_media_status %s" % (self._player, status.player_state))
        if status.player_state != 'PLAYING':
            logging.debug("[%s] Skipping due to status" % (self._player,))
            return
        
        song = status.media_metadata.get('songName', status.media_metadata['title'])
        self._lock.acquire(True)
        try:
            if song == self._song:
                logging.debug("[%s] Skipping due to same song again (%s)" % (self._player, self._song))
                return
            self._song = song
        finally:
            self._lock.release()

        logging.info("Posting song %s" % (self._song, ))
        artist = None
        try:
            artist = status.media_metadata['artist']
        except:
            logging.exception("Failed to get artist")
            
        image = ""
        try:
            image = status.media_metadata['images'][0]['url']
        except:
            logging.exception("Failed to get image")
        try:
            self.postSong(self.get_source(status), artist, song, image)
        except Exception as e:
            logging.exception("Failed to post song")

    def postSong(self, source, artist, song_name, image=None):
        logging.info("[%s]\t%s - %s (%s)" % (self._player, artist, song_name, image))
        text = song_name
        if not artist == None:
            text = "{} - {}".format(song_name, artist)
        self._bot.sayEx(source, text, image, self._player)

def active_devices():
    return pychromecast.get_chromecasts()

class ChromecastManager(object):
    def __init__(self, bot):
        self.active_list = {}
        self.bot = bot

    def poll(self):
        for chromecast in active_devices():
            if chromecast.uuid in self.active_list:
                continue
            self.register(chromecast)

    def register(self, cs):
        chromecast = cs.device.friendly_name
        l = ChromecastListener(chromecast, self.bot)
        if cs is None:
            logging.error("[%s] Registration failed" % (chromecast, ))
            return
        cs.wait()
        mc = cs.media_controller
        mc.register_status_listener(l)
        logging.info("[%s] Registered" % (chromecast, ))
        self.active_list[cs.uuid] = [l, mc]

def main():
    m = ChromecastManager(bot.Bot())
    while True:
        m.poll()
        sleep(POLL_INTERVAL)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

