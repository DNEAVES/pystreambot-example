#!/usr/bin/env python3.10

import pathlib
import multiprocessing
import subprocess

# This is the core twitch bot. It runs the chatbot and eventsub
from twitchbot import bot_main

# This uses spotifycli to get the currently playing track, and spit it out to a file
# OBS then reads this file
from spotifystreamtext import spot_main

# This is just an OBS webhook on a timer
from obstimers import obs_main


if __name__ == '__main__':
    this_dir = pathlib.Path(__file__).parent.absolute()

    # All this file does is stops NGINX and starts Caddy.
    # I don't even know why NGINX is running on startup.
    subprocess.run(f"{this_dir}/enable_caddy.sh",
                   shell=True,
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    multiprocessing.set_start_method('forkserver')

    # DO NOT ADD PARENTHESIS TO TARGET FUNCTIONS. MULTIPROCESSING DOES NOT LIKE THIS
    p = multiprocessing.Process(target=spot_main, name="dnpybot_spot")
    o = multiprocessing.Process(target=obs_main, name="dnpybot_obs")
    b = multiprocessing.Process(target=bot_main, name="dnpybot_bot")
    p.start()
    o.start()
    b.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        b.kill()
        p.kill()
        o.kill()
        quit()
