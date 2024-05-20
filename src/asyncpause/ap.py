import asyncio
import os.path
import pickle
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional, Any

import aiofiles


class QueueStatus(Enum):
    EMPTY = -1
    CLEAN = 0
    CHANGED = 8


class CallArgs:
    def __init__(self, at: datetime, args, kwargs):
        self.id = uuid.uuid4()
        self.args = args
        self.kwargs = kwargs
        self.at = at

    def __repr__(self):
        return f"CallArgs({self.args}, {self.kwargs} at {self.at} / {self.id}"


class AsyncPause:
    def __init__(self, call: Callable, filepath=None, no_load=False, in_memory=False):
        self._filename = filepath or f".{call.__name__.lower()}.paused"
        self._queue: list[CallArgs] = []
        self._status = QueueStatus.EMPTY
        self._call = call
        self._in_memory = in_memory
        if not no_load:
            self.load()

    def set(self, at: datetime | timedelta | float | int, *args: Any, **kwargs: Any):
        if isinstance(at, timedelta):
            at = datetime.now() + at
        elif isinstance(at, (float, int)):
            at = datetime.now() + timedelta(seconds=at)
        arg = CallArgs(at, args, kwargs)
        self._queue.append(arg)
        self._status = QueueStatus.CHANGED

    def remove(self, arg: CallArgs):
        self._queue.remove(arg)
        self._status = QueueStatus.CHANGED

    async def save(self):
        if not self._in_memory:
            async with aiofiles.open(self._filename, "wb") as f:
                await f.write(pickle.dumps(self._queue))
        self._status = QueueStatus.CLEAN

    def load(self):
        if self._in_memory or not os.path.exists(self._filename):
            self._status = QueueStatus.CLEAN
            return
        with open(self._filename, "rb") as f:
            data = pickle.load(f)
        self._queue = data
        self._status = QueueStatus.CLEAN

    async def async_load(self):
        if self._in_memory or not os.path.exists(self._filename):
            self._status = QueueStatus.CLEAN
            return
        async with aiofiles.open(self._filename, "rb") as f:
            data = await f.read()
        self._queue = pickle.loads(data)
        self._status = QueueStatus.CLEAN

    async def background_saver(self):
        while True:
            if self._status == QueueStatus.CHANGED:
                await self.save()
                self._status = QueueStatus.CLEAN
            await asyncio.sleep(1)

    async def background_runner(self, sleep_on_empty: float = 1):
        while True:
            for arg in self._queue:
                if arg.at < datetime.now():
                    self.remove(arg)
                    try:
                        await self._call(*arg.args, **arg.kwargs)
                    except Exception as e:
                        print(f"Error: {e}")
                        self._queue.append(arg)
                        self._status = QueueStatus.CHANGED
            if not self._queue:
                await asyncio.sleep(sleep_on_empty)
            else:
                await asyncio.sleep(0.001)

    async def start_background(self):
        if not self._in_memory:
            _ = asyncio.create_task(self.background_saver())
        _ = asyncio.create_task(self.background_runner())

    @staticmethod
    async def setup(call: Callable, filepath=None, in_memory=False):
        s = AsyncPause(call=call, filepath=filepath, in_memory = in_memory)
        await s.start_background()
        return s


if __name__ == "__main__":

    async def main():
        async def aprint(*args, **kwargs):
            print(*args, **kwargs)

        d = await AsyncPause.setup(aprint)
        d.set(datetime.now(), "Hello, world!")
        d.set(timedelta(seconds=5), "Hello, world! 5 sec spent!")
        d.set(timedelta(seconds=1), "Hello, world after a second!")
        d.set(timedelta(seconds=2))
        await asyncio.sleep(6)

    asyncio.run(main())
