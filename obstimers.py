#!/usr/bin/env python3.10

import time
from obswebsocket import obsws
from obswebsocket import requests as obsreq

from color import color
from private import OBS_HOST, OBS_PORT, OBS_PASSWORD

ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)


def obs_main():
    print(f"{color('[OBSWebook]', 'obs')} OBSBanner module running!")
    print(f"{color('[OBSWebook]', 'obs')} OBSBanner module is ready!")
    while True:
        time.sleep(600)
        print(f"{color('[OBSWebook]', 'obs')} Displaying Website")
        ws.connect()
        ws.call(obsreq.SetSceneItemProperties('Black Bar Other', scene_name="UI", visible=True))
        ws.call(obsreq.SetSceneItemProperties('Web', scene_name="UI", visible=True))
        ws.call(obsreq.SetSceneItemProperties('Website', scene_name="UI", visible=True))
        time.sleep(10)
        ws.call(obsreq.SetSceneItemProperties('Website', scene_name="UI", visible=False))
        ws.call(obsreq.SetSceneItemProperties('Web', scene_name="UI", visible=False))
        ws.call(obsreq.SetSceneItemProperties('Black Bar Other', scene_name="UI", visible=False))
        ws.disconnect()
