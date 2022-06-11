#!/usr/bin/env python3.10

import subprocess
import time

from color import color


def spot_main():
    print(f"{color('[Spotify]', 'spotify')} SpotifyText module running!")
    print(f"{color('[Spotify]', 'spotify')} SpotifyText module is ready!")
    while True:
        with open("/home/dneaves/.spotifybuffer", "r") as r:
            old_song = r.read()
        song = subprocess.run("spotifycli --status", shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").replace('-', '|', 1).replace('\n', '')
        time.sleep(.5)
        if song != old_song:
            with open("/home/dneaves/.spotifybuffer", "w") as f:
                f.write(song)
            print(f"{color('[Spotify]', 'spotify')} {song}")
            subprocess.run("cp /home/dneaves/.spotifybuffer /home/dneaves/.spotify_now_playing.txt", shell=True)
        time.sleep(1)


if __name__ == '__main__':
    spot_main()
