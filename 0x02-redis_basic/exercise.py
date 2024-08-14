#!/usr/bin/env python3
"""
doc for module where i am implementing redis concepts
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        method_name = method.__qualname__
        self._redis.incr(method_name)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to log input arguments and output results of a method."""
    input_key = method.__qualname__ + ":inputs"
    output_key = method.__qualname__ + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))
        return result
    return wrapper


def replay(method: Callable) -> None:
    """Display call history for a method, including inputs and outputs."""
    methd = method.__qualname__
    input_key = f"{methd}:inputs"
    output_key = f"{methd}:outputs"

    inputs = method.__self__._redis.lrange(input_key, 0, -1)
    outputs = method.__self__._redis.lrange(output_key, 0, -1)

    print(f"{methd} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{methd}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")


class Cache:
    """Class to interact with Redis for storing
    and retrieving data with call tracking."""
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis and return the unique key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float]:
        """Retrieve data from Redis and apply optional conversion function."""
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """Retrieve data as a string."""
        return self.get(key, fn=lambda data: data.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """Retrieve data as an integer."""
        return self.get(key, fn=int)
