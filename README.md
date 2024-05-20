# asyncpause

Welcome to `asyncpause`! This nifty little Python library is here to make sure your async functions get called exactly when you want them to, even if your program decides to take a little nap in between. With `asyncpause`, you can schedule async function calls to run at specific times or after certain delays, and it will ensure they are executed even after a restart. Say goodbye to missed calls and hello to punctuality!

## Features

- Schedule async function calls with ease.
- Save call details to disk to survive restarts.
- Load and execute scheduled calls automatically.
- Supports delays in seconds, timedeltas, or specific datetime objects.

## Installation

You can install `asyncpause` via pip:

```sh
pip install asyncpause
```

## Usage

Here's a quick example to get you started. Let's schedule some functions and watch the magic happen.

```python
import asyncio
from datetime import datetime, timedelta
from asyncpause import AsyncPause

async def main():
    async def aprint(*args, **kwargs):
        print(*args, **kwargs)

    d = await AsyncPause.setup(aprint)
    # you can also pass a filepath to save the scheduled calls
    # or in_memory=True to keep them in memory :)
    d.set(datetime.now(), "Hello, world!")
    d.set(timedelta(seconds=5), "Hello, world! 5 sec spent!")
    d.set(timedelta(seconds=1), "Hello, world after a second!")
    d.set(timedelta(seconds=2))
    await asyncio.sleep(6)

asyncio.run(main())
```

In this example, the `aprint` function its just an example. Just run this script, and watch your console get filled with timely greetings.

## How It Works

1. **Initialization**: Create an `AsyncPause` object with your target function.
2. **Scheduling**: Use the `set` method to schedule your function calls. You can specify a delay in seconds, a `timedelta`, or a specific `datetime`.
3. **Persistence**: The library saves the scheduled calls to a file (or keeps them in memory if you prefer).
4. **Execution**: It runs the scheduled calls at the right time, even after restarts.

## Why asyncpause?

Because sometimes you just need your async functions to be fashionably late, not never! This library handles all the tedious work of saving, loading, and running your scheduled functions, so you can focus on writing great code without worrying about time.

## Contributing

Feel free to fork this repository, make some changes, and submit a pull request. Whether it's fixing bugs, adding features, or just improving documentation, all contributions are welcome!

## License

This project is licensed under The Unlicense.

## Conclusion

`asyncpause` is your go-to tool for scheduling async function calls in Python. It's reliable, easy to use, and ensures that your functions are called when they should be, no matter what. So why wait? Install `asyncpause` today and give your async functions the punctuality they deserve!

---

_P.S. Why was the async function always on time? Because it knew how to `await` its turn!_
