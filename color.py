#!/usr/bin/env python3.10

def color(text: str, color: str = ""):
        match color:
            case "orange":
                colorint = 208
            case "cyan":
                colorint = 51
            case "lime":
                colorint = 40
            case "red":
                colorint = 160
            case "magenta":
                colorint = 201

            case "twitch":
                colorint = 93
            case "event":
                colorint = 221
            case "spotify":
                colorint = 70
            case "obs":
                colorint = 248

            case _:
                colorint = 15

        return f"\033[38;5;{colorint}m{text}\033[0;0m"
