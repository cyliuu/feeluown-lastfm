# 参考https://github.com/mopidy/mopidy-scrobbler/blob/master/mopidy_scrobbler/frontend.py
import asyncio
import logging
import time

import pylast

logger = logging.getLogger(__name__)


API_KEY = '2236babefa8ebb3d93ea467560d00d04'
API_SECRET = '94d9a09c0cd5be955c4afaeaffcaefcd'
USERNAME = ''
PASSWORD = ''


PYLAST_ERRORS = tuple(
    getattr(pylast, exc_name)
    for exc_name in (
        'ScrobblingError', 'NetworkError', 'MalformedResponseError', 'WSError')
    if hasattr(pylast, exc_name)
)


class ScrobServer():
    def __init__(self, app):
        self._app = app
        self.last_fm = None
        self.time_position = None
        self.last_start_time = None
        self.last_music_model = None

        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._on_start)

    def _on_start(self):
        try:
            self.last_fm = pylast.LastFMNetwork(
                api_key=API_KEY, api_secret=API_SECRET,
                username=USERNAME,
                password_hash=pylast.md5(PASSWORD))
            logger.debug('Scrobbler connected to Last.fm')
        except PYLAST_ERRORS as e:
            logger.error('Error during Last.fm setup: %s', e)
        else:
            self._app.player.position_changed.connect(self.set_time_position)
            self._app.playlist.song_changed.connect(self.song_changed)

    def set_time_position(self, value):
        self.time_position = value

    def song_changed(self, music_model):
        asyncio.ensure_future(self._song_changed(self.last_music_model,
                                                 self.last_start_time,
                                                 music_model))
        self.last_music_model = music_model

    async def _song_changed(self, last_music_model, last_start_time, music_model):
        loop = asyncio.get_event_loop()
        if last_music_model:
            await loop.run_in_executor(None, self._song_playback_ended,
                                       last_music_model, last_start_time)
        if music_model:
            await loop.run_in_executor(None, self._song_playback_started,
                                       music_model)

    def _song_playback_started(self, song):
        self.last_start_time = int(time.time())
        logger.debug('Now playing track: %s - %s', song.artists_name, song.title)
        try:
            self.last_fm.update_now_playing(
                song.artists_name,
                (song.title or ''),
                album_artist=song.album.artists_name,
                duration=str(song.duration // 1000 or 0))
        except PYLAST_ERRORS as e:
            logger.warning('Error submitting playing track to Last.fm: %s', e)

    def _song_playback_ended(self, song, start_time):
        duration = song.duration // 1000 or 0
        time_position = self.time_position
        if not time_position:
            time_position = duration
        if duration < 30:
            logger.debug('Track too short to scrobble. (30s)')
            return
        if time_position < duration // 2 and time_position < 240:
            logger.debug(
                'Track not played long enough to scrobble. (50% or 240s)')
            return
        logger.info('Scrobbling track: %s - %s', song.artists_name, song.title)
        try:
            self.last_fm.scrobble(
                song.artists_name,
                (song.title or ''),
                str(start_time),
                album=song.album_name.strip(),
                duration=str(duration))
        except PYLAST_ERRORS as e:
            logger.warning('Error submitting played track to Last.fm: %s', e)
