#!/usr/bin/env python3
import asyncio
import dataset
import datetime

class Task(object):
    def __init__(self, chat_id, goal, callback, delay=25*60):

        self.asyncio_handle = asyncio.get_event_loop().call_later(
            delay,
            callback)
        self.goal = goal
        self.chat_id = chat_id
        self.start_time = datetime.datetime.now()
        with dataset.connect("sqlite:///tasks.db") as d:
            d["tasks"].insert(
                dict(
                    chat_id=self.chat_id,
                    start_time=self.start_time,
                    end_time=None,
                    goal=self.goal,
                    completed=False,
                ))
        print("Finished geting myself.")


    @asyncio.coroutine
    def cancel(self):
        self.asyncio_handle.cancel()

    def complete(self):
        """This function should be called to complete a task.

        Tasks should only complete once the delay is up, but no
        checking is done to make sure this is the case

        TODO make this automatic (maybe inherit from asyncio.Handler?).

        """

        with dataset.connect("sqlite:///tasks.db") as d:
            d["tasks"].update(
                dict(
                    chat_id=self.chat_id,
                    start_time=self.start_time,
                    completed=True,
                    end_time=datetime.datetime.now(),
                ), ['chat_id', 'start_time'])



    def time_remaining(self):
        """Return time remaining in Task."""
        return self.asyncio_handle._when - asyncio.get_event_loop().time()
