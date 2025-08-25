
import os
import time
from functools import wraps




def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start_time) * 1000  # 毫秒
        print(f"⏱️ {func.__name__} 耗时: {elapsed:.2f}ms")
        return result
    return wrapper