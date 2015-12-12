#!/usr/bin/env python3
import asyncio
import yaml
import telepot
from telepot.async.delegate import create_open
from telepot.delegate import per_chat_id

from tomatotimertgbot import Tomato

if __name__ == "__main__":
    config = yaml.load(open("config.yml", "r"))
    bot = telepot.async.DelegatorBot(
        config["telegram_bot_id"],
        [
            (per_chat_id(), create_open(
                Tomato, timeout=72*3600)),
        ])

    loop = asyncio.get_event_loop()
    loop.create_task(bot.messageLoop())
    loop.run_forever()
    

