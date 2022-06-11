#!/usr/bin/env python3.10
import twitchio
from twitchio.ext import commands, eventsub

import secrets
import string
from datetime import datetime
import time
import sys
import urllib.request
import re
import subprocess
from obswebsocket import obsws
from obswebsocket import requests as obsreq
from gtts import gTTS

# I'm regex-ing particular bad words. Yep.
from badwords import bad_words, web_words

from color import color
from private import (BOT_ACCESS_TOKEN,
                     BOT_CLIENT_ID,
                     BOT_API_SECRET,
                     BOT_NICK,
                     DN_ID,
                     DN_API_SECRET,
                     CHANNEL,
                     CHANNEL_ID,
                     OBS_HOST,
                     OBS_PORT,
                     OBS_PASSWORD,
                     WEBSITE)

ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)

password = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(99))


esbot = commands.Bot.from_client_credentials(client_id=DN_ID,
                                             client_secret=DN_API_SECRET)

esclient = eventsub.EventSubClient(esbot,
                                   webhook_secret=password,
                                   callback_route=WEBSITE)


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=BOT_ACCESS_TOKEN,
            client_id=BOT_CLIENT_ID,
            client_secret=BOT_API_SECRET,
            nick=BOT_NICK,
            prefix="!",
            initial_channels=[CHANNEL],
        )
        # Here just to be a property. Gets overwritten later.
        self.time_start: datetime = datetime.now()

    async def __ainit__(self) -> None:
        print(f"{color('[EventSub]', 'event')} Starting webhook.")
        self.loop.create_task(esclient.listen(port=4000))

        # Future function, awaiting pull request approval.
        # await esclient.delete_all_active_subscriptions()

        print(f"{color('[EventSub]', 'event')} Subscribing to events...")

        try:
            await esclient.subscribe_channel_stream_start(broadcaster=CHANNEL_ID)
            await esclient.subscribe_channel_update(broadcaster=CHANNEL_ID)
            print(f"{color('[EventSub]', 'event')} ...miscellaneous events: Done!")
        except twitchio.HTTPException as e:
            print(f"{color('[EventSub]', 'event')} {color(f'Error when subscribing to misc channel data: {e}', 'red')}")

        try:
            await esclient.subscribe_channel_follows(broadcaster=CHANNEL_ID)
            print(f"{color('[EventSub]', 'event')} ...follow events: Done!")
        except twitchio.HTTPException as e:
            print(f"{color('[EventSub]', 'event')} {color(f'Error when subscribing to follows: {e}', 'red')}")

        try:
            await esclient.subscribe_channel_subscriptions(broadcaster=CHANNEL_ID)
            # Also future functions, awaiting the same pull request approval.
            # await esclient.subscribe_channel_subscription_gifts(broadcaster=CHANNEL_ID)
            # await esclient.subscribe_channel_subscription_messages(broadcaster=CHANNEL_ID)
            print(f"{color('[EventSub]', 'event')} ...subscribe events: Done!")
        except twitchio.HTTPException as e:
            print(f"{color('[EventSub]', 'event')} {color(f'Error when subscribing to subscriptions: {e}', 'red')}")

        try:
            await esclient.subscribe_channel_cheers(broadcaster=CHANNEL_ID)
            print(f"{color('[EventSub]', 'event')} ...bits events: Done!")
        except twitchio.HTTPException as e:
            print(f"{color('[EventSub]', 'event')} {color(f'Error when subscribing to bits: {e}', 'red')}")

        try:
            await esclient.subscribe_channel_raid(to_broadcaster=CHANNEL_ID)
            print(f"{color('[EventSub]', 'event')} ...raid events: Done!")
        except twitchio.HTTPException as e:
            print(f"{color('[EventSub]', 'event')} {color(f'Error when subscribing to raids: {e}', 'red')}")

    async def event_ready(self):
        print(f"{color('[TwitchBot]', 'magenta')} TwitchBot module is ready!")

    async def event_message(self, ctx):
        try:
            if not (ctx.author.is_mod or (ctx.author.name.lower() == CHANNEL) or (ctx.author.name.lower() == BOT_NICK)):
                if bad_words(ctx.content.lower()):
                    await ctx.channel.timeout(ctx.author.name, 60, "Bad word detected. Put soap in that mouth.")
                if web_words(ctx.content.lower()):
                    await ctx.channel.timeout(ctx.author.name, 3, "No weblinks please, I'm allergic!")
        except AttributeError as e:
            print(f"{color('[TwitchBot]', 'magenta')} {color(f'Error with chat message: {e}', 'red')}")
        print(f"{color('[TwitchChat]', 'twitch')} {ctx.author.name}: {ctx.content}")
        await self.handle_commands(ctx)

    # Updawg
    @commands.command(name="uptime")
    async def uptime(self, ctx):
        time_up = self.time_start.time()
        await ctx.send(f"We've been here for {time_up}!")

    # Are You Still There?
    @commands.command(name='test')
    async def test(self, ctx):
        if ctx.author.name.lower() == CHANNEL:
            await ctx.send("Test Successful! Hello!")
        else:
            await ctx.channel.send("Sorry, you're not allowed to use this bot command!")

    # SocialCommands
    @commands.command(name='twitter')
    async def twitter(self, ctx):
        await ctx.channel.send("Follow me on Twitter here: https://twitter.com/dneaves")

    @commands.command(name='latestvideo', aliases=['lastvideo', 'lastvid', 'newvid', 'latestvid', 'newvideo'])
    async def latestvideo(self, ctx):
        html = urllib.request.urlopen("https://www.youtube.com/channel/UCMGZhwKg7rSTD7a3KzgpKbA/videos")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        lastvid = "https://www.youtube.com/watch?v=" + video_ids[0]
        await ctx.channel.send("Here's my last Youtube Gaming video!")
        await ctx.channel.send(lastvid)

    @commands.command(name='links', aliases=['website', 'socials'])
    async def links(self, ctx):
        await ctx.channel.send("Find all my links here: https://dneaves.github.io")

    @commands.command(name='shutdown')
    async def shutdown(self, ctx):
        if ctx.author.name.lower() != CHANNEL:
            return await ctx.send("Sorry, you're ESPECIALLY not allowed to use this bot command!")
        else:
            print("Shutting Down")
            sys.exit()


def obs_event(event_message,
              other_message=None,
              sound=True,
              duration=3):

    default_message = "[user] did [thing]! Wow!"
    print(f"{color('[EventSub]', 'event')} {event_message}")
    if other_message:
        print(f"{color('[EventSub]', 'event')} {other_message}")
    if sound:
        subprocess.run(f"ffplay -nodisp -autoexit {sys.path[0]}/Airhorn2.wav",
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    ws.connect()
    ws.call(obsreq.SetTextFreetype2Properties('EventMsg', text=event_message))
    ws.call(obsreq.SetSceneItemProperties('Orange Bar Alerts', scene_name="UI", visible=True))
    ws.call(obsreq.SetSceneItemProperties('Thumb', scene_name="UI", visible=True))
    ws.call(obsreq.SetSceneItemProperties('EventMsg', scene_name="UI", visible=True))

    time.sleep(duration)
    if other_message:
        if bad_words(other_message):
            other_message = "Bad words detected, message deleted."
        ws.call(obsreq.SetSceneItemProperties('EventMsg', scene_name="UI", visible=False))
        time.sleep(.5)
        ws.call(obsreq.SetTextFreetype2Properties('EventMsg', text=other_message))
        ws.call(obsreq.SetSceneItemProperties('EventMsg', scene_name="UI", visible=True))
        tts = gTTS(other_message, 'ie', lang='en')
        tts.save('/home/dneaves/.speechfile')
        subprocess.run("ffplay -nodisp -autoexit /home/dneaves/.speechfile",
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
    ws.call(obsreq.SetSceneItemProperties('EventMsg', scene_name="UI", visible=False))
    ws.call(obsreq.SetSceneItemProperties('Thumb', scene_name="UI", visible=False))
    ws.call(obsreq.SetSceneItemProperties('Orange Bar Alerts', scene_name="UI", visible=False))
    ws.call(obsreq.SetTextFreetype2Properties('EventMsg', text=default_message))
    ws.disconnect()


# Run the bot
def bot_main():
    print(f"{color('[TwitchBot]', 'magenta')} TwitchBot module running!")
    bot = Bot()
    bot.loop.run_until_complete(bot.__ainit__())

    @esbot.event()
    async def event_eventsub_notification_stream_start(payload):
        bot.time_start = payload.data.started_at

    @esbot.event()
    async def event_eventsub_notification_channel_update(payload):
        title = payload.data.title
        game = payload.data.category_name
        print(f"{color('[EventSub]', 'event')} New Channel Data: {title} : {game}")

    @esbot.event()
    async def event_eventsub_notification_follow(payload):
        person = payload.data.user.name
        event_message = f"{person} is a new follower! Welcome!"
        obs_event(event_message)

    @esbot.event()
    async def event_eventsub_notification_subscription(payload):
        person = payload.data.user.name
        tier = str(payload.data.tier)[0]
        gift = payload.data.is_gift
        if gift:
            sound = False
            event_message = f"{person} was gifted a tier {tier} subscription!"
            duration = 1
        else:
            sound = True
            event_message = f"{person} subscribed with tier {tier}!"
            duration = 3
        obs_event(event_message, sound=sound, duration=duration)

    # All of this is awaiting PR
    # @esbot.event()
    # async def event_eventsub_notification_subscription_gift(payload):
    #     if not payload.data.is_anonymous:
    #         person = payload.data.user.name
    #     else:
    #         person = "Anonymous"
    #     tier = str(payload.data.tier)[0]
    #     total = payload.data.total
    #     cumulative = payload.data.cumulative
    #     if cumulative:
    #         event_message = f"{person} gifted {total} tier {tier} subscriptions! ({cumulative} total)"
    #     else:
    #         event_message = f"{person} gifted {total} tier {tier} subscriptions!"
    #     obs_event(event_message)
    #
    # @esbot.event()
    # async def event_eventsub_notification_subscription_message(payload):
    #     person = payload.data.user.name
    #     tier = str(payload.data.tier)[0]
    #     cumulative = payload.data.cumulative
    #     streak = payload.data.streak
    #     duration = payload.data.duration
    #     message = payload.data.message
    #     if bad_words(message):
    #         message = "Bad words detected, message deleted."
    #     if cumulative != "1":
    #         if duration == "1" or duration == "0":
    #             if streak:
    #                 event_message = f"{person} resubscribed! (tier {tier}, {streak} month streak, {cumulative} total)"
    #             else:
    #                 event_message = f"{person} resubscribed! (tier {tier}, {cumulative} months total)"
    #         else:
    #             if streak:
    #                 event_message = f"{person} resubscribed! (duration {duration} months, tier {tier}, {streak} month streak, {cumulative} total)"
    #             else:
    #                 event_message = f"{person} resubscribed! (duration {duration} months, tier {tier}, {cumulative} months total)"
    #         obs_event(event_message, other_message=message)

    @esbot.event()
    async def event_eventsub_notification_cheer(payload):
        if not payload.data.is_anonymous:
            person = payload.data.user.name
        else:
            person = "Anonymous"
        message = payload.data.message
        if bad_words(message):
            message = "Bad words detected, message deleted."
        bits = payload.data.bits
        event_message = f"{person} has cheered {bits} bits!"
        obs_event(event_message, other_message=message)

    @esbot.event()
    async def event_eventsub_notification_raid(payload):
        person = payload.data.raider.name
        viewers = payload.data.viewer_count
        event_message = f"Incoming raid from {person} with {viewers} viewers!"
        obs_event(event_message)

    bot.run()

# This is here for only testing this file, instead of starting up the other stuff too.
if __name__ == '__main__':
    bot_main()
