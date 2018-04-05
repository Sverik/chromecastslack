from slackclient import SlackClient
import json
import os
import logging

ICON = ":guitar:"

class Bot(object):
    def __init__(self):
        self._client = SlackClient(self._token())
        self._icon = ICON
        self._client.rtm_connect()

    def _token(self):
        return os.environ['SLACKBOT_TOKEN']
    
    def _channel(self):
        return os.environ.get('CHANNEL', 'musicreactions')

    def say(self, username, message):
        logging.debug("Saying as {}: {}".format(username, message))
        self._client.rtm_send_message(self._channel, message)

    def sayEx(self, username, text, image, footer):
        logging.debug("Extra saying as {}: {}, {}, {}".format(username, text, image, footer))
        d = {'thumb_url': image, 'text': text, "footer": footer, "fallback": text}
        self._client.api_call("chat.postMessage", channel=self._channel(), username=username, as_user="false", icon_emoji=self._icon, attachments=json.dumps([d]))

