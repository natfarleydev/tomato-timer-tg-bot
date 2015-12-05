#!/usr/bin/env python3
import asyncio
import telepot
from telepot.async.delegate import create_open
from telepot.delegate import per_chat_id

import yaml
import datetime
import random
import math

def format_seconds_as_mm_ss(seconds):
    return "{}:{:02}".format(
        math.floor(seconds/60.0), math.floor(seconds) % 60)


class PomodoroHandler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(PomodoroHandler, self).__init__(seed_tuple, timeout)
        self._current_pomodoro_handler = None

    @asyncio.coroutine
    def on_message(self, msg):
        if "/tomato" in msg["text"]:
            yield from self.sender.sendMessage("I AM A TOMATO!!!")
        if "/pomodorostart" in msg["text"]:
            yield from self.pomodoro_begin(msg)
        if "/timeleft" in msg["text"]:
            yield from self.pomodoro_time_left(msg)
        if "/cancel" in msg["text"]:
            yield from self.pomodoro_cancel(msg)
        if "/currentgoal" in msg["text"]:
            yield from self.pomodoro_current_goal(msg)
        if "/compliment" in msg["text"]:
            yield from self.compliment(msg)

    @asyncio.coroutine
    def pomodoro_current_goal(self, msg):
        try:
            yield from self.sender.sendMessage(self.current_goal)
        except AttributeError:
            yield from self.sender.sendMessage("NO GOAL.")

    @asyncio.coroutine
    def pomodoro_cancel(self, msg):
        if self._current_pomodoro_handler is not None:
            yield from self.sender.sendMessage("TIMER CANCELLED.")
            self._current_pomodoro_handler.cancel()
            self._current_pomodoro_handler = None
        else:
            yield from self.sender.sendMessage("TIMER NOT STARTED.")
            

    @asyncio.coroutine
    def compliment(self, msg):
        compliments = [
            "YOU ARE NOT A TOMATO.",
            "GOOD JOB.",
            "YOU WORK HARD.",
            "MAYBE YOU FAIL. MAYBE NOT.",
            "I AM CONFUSED.",
            "YOUR COMMAND OF LANGUAGE IS ... EXISTENT.",
            "GO HUMAN GO.",
            "YOUR HAIR IS INTERESTING.",
            "GET BACK TO WORK." if self._current_pomodoro_handler is not None else "BREAK OVER.",
            ]
        yield from self.sender.sendMessage(random.choice(compliments))


    def pomodoro_time_left(self, msg):
        if self._current_pomodoro_handler is not None:
            yield from self.sender.sendMessage(
                "{} LEFT TO ACHIEVE ".format(
                format_seconds_as_mm_ss(
                    self._current_pomodoro_handler._when-asyncio.get_event_loop().time()))+self.current_goal)
        else:
            yield from self.sender.sendMessage(
                "TIMER NOT STARTED.")

    @asyncio.coroutine
    def pomodoro_end(self, msg):
        yield from self.sender.sendMessage("POMODORO END!")
        yield from self.sender.sendMessage(
            "YOU ACHIEVE "+self.current_goal+"?")

    @asyncio.coroutine
    def pomodoro_begin(self, msg):
        yield from self.sender.sendMessage("YOUR GOAL:")
        self.listener.set_options(timeout=30)
        try:
            current_goal_msg = yield from self.listener.wait()
        except telepot.helper.WaitTooLong as e:
            yield from self.sender.sendMessage("TOO SLOW.")
            raise(e)
        except Exception as e:
            yield from self.sender.sendMessage("MALFUNCTION.")
            raise(e)

        self.listener.set_options(timeout=None)
        self.current_goal = current_goal_msg["text"].replace("@tomato_timer_bot ", "")
        print(self.current_goal)

        h = asyncio.get_event_loop().call_later(
            60*25,
            lambda: asyncio.async(self.pomodoro_end(msg)))
        self._current_pomodoro_handler = h
        
        yield from self.sender.sendMessage("POMODORO BEGIN!")

if __name__ == "__main__":
    config = yaml.load(open("config.yml", "r"))
    bot = telepot.async.DelegatorBot(
        config["telegram_bot_id"],
        [
            (per_chat_id(), create_open(
                PomodoroHandler, timeout=72*3600)),
        ])

    loop = asyncio.get_event_loop()
    loop.create_task(bot.messageLoop())
    loop.run_forever()
    

