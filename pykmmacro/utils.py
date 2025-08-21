import itertools
import random
import time
from typing import Any, Callable, Final, Generator, Iterable

#=============================================================================
# Constant

_DELAY_MS_FOR_A_MOMENT: Final[int] = 100
_DELAY_MS_FOR_ENSURE: Final[int] = 300
_DELAY_MS_FOR_A_TICK: Final[int] = 50

#=============================================================================
# Exception

class MyError(Exception):
    pass

class MyFailAlwaysError(MyError):
    pass

class MyTimeoutError(MyError):
    pass

#=============================================================================
# Private functions

#=============================================================================
# Miscellaneous

def my_fail_always():
    raise MyFailAlwaysError()

def my_assert_eq(l, r, *rest): # type: ignore
    assert l == r, (l, r, *rest)

def my_unique[S, T](seq: Iterable[S], *, key_func: Callable[[S], T]=lambda x: x) -> Iterable[S]:
    """
    Remove duplicated items in a sequence.
    If `key_func` is specified, the value of `key_func(item)` is used to distinguish an item from another item.
    """
    is_dedup: set[T] = set()
    def generate_result():
        for value in seq:
            key = key_func(value)
            if key in is_dedup:
                continue
            is_dedup.add(key)
            yield value
    return generate_result()

def my_random() -> float:
    """
    use the average as *approximate* Gaussian random value
    https://k11i.biz/blog/2016/11/05/approximate-gaussian-rng/
    """
    num = 100 # with no foundation
    acc = 0.0
    for _ in range(num):
        acc += random.random()
    result = acc / num
    assert 0.0 <= result and result < 1.0
    return result

#=============================================================================
# Time

def my_get_str_timestamp() -> str:
    return time.strftime("%Y/%m/%d %H:%M:%S")

def my_get_timestamp_ms() -> int:
    return time.time_ns() // (1000 * 1000)

def my_sleep_ms(period_ms: int):
    assert period_ms > 0
    time.sleep(period_ms / 1000)

def my_sleep_with_random(period_ms: int, /, *, variation_ratio: float = 0.4):
    assert period_ms > 0
    assert 0 <= variation_ratio and variation_ratio < 1.0
    variation = period_ms * variation_ratio # may be zero
    period = period_ms - variation / 2 + variation * my_random()
    time.sleep(period / 1000) # use `time.sleep()` directly to make leaf period (<=1ms) effective

def my_sleep_a_moment():
    my_sleep_with_random(_DELAY_MS_FOR_A_MOMENT, variation_ratio=0.2)

def g_sleep_with_random(period_ms: int, /, *, variation_ratio: float = 0.4) -> Generator[None]:
    assert period_ms > 0
    assert 0 <= variation_ratio and variation_ratio < 1.0
    variation = period_ms * variation_ratio # may be zero
    period = period_ms - variation / 2 + variation * my_random()
    limit = my_get_timestamp_ms() + period
    while (now := my_get_timestamp_ms()) < limit - _DELAY_MS_FOR_A_TICK:
        yield
        my_sleep_ms(_DELAY_MS_FOR_A_TICK)
    yield # use `yield` at least once to avoid long time blocking
    period_at_last = limit - now
    if period_at_last > 0:
        time.sleep(period_at_last / 1000) # use `time.sleep()` directly to make leaf period (<=1ms) effective

def g_sleep(period_ms: int) -> Generator[None]:
    yield from g_sleep_with_random(period_ms, variation_ratio=0.0)

def g_sleep_a_moment() -> Generator[None]:
    yield from g_sleep_with_random(_DELAY_MS_FOR_A_MOMENT, variation_ratio=0.2)

def g_sleep_to_ensure() -> Generator[None]:
    yield from g_sleep_with_random(_DELAY_MS_FOR_ENSURE, variation_ratio=0.2)

def g_with_timeout(timeout_ms: int, func: Callable[Any, Any], *args, **kwargs) -> Generator[None, Any]: # type: ignore
    # NOTE: `func` should not be a generator.
    assert timeout_ms > 0
    limit = my_get_timestamp_ms() + timeout_ms
    while True:
        # call `func()` before timeout judgement
        timestamp = my_get_timestamp_ms() # capture this timing (before calling `func`)
        ret = func(*args, **kwargs)
        if ret is not None:
            return ret
        if timestamp > limit:
            raise MyTimeoutError(f"{timeout_ms=} / {func.__name__}()")
        yield from g_sleep(_DELAY_MS_FOR_A_TICK)

def g_with_timeout_until(timeout_ms: int, func: Callable[Any, Any], *args, **kwargs): # type: ignore
    yield from g_with_timeout(timeout_ms, lambda: func(*args, **kwargs) or None)

def g_with_timeout_while(timeout_ms: int, func: Callable[Any, Any], *args, **kwargs): # type: ignore
    yield from g_with_timeout_until(timeout_ms, lambda: not func(*args, **kwargs))

#=============================================================================
# Geometry

def is_in_rect(pos: tuple[int, int], rect) -> bool:
    assert rect.right - rect.left > 0
    assert rect.bottom - rect.top > 0
    x, y = pos
    return rect.left <= x and x < rect.right and rect.top <= y and y < rect.bottom

def is_rect_intersect(rect1, rect2) -> bool:
    assert rect1.right - rect1.left > 0
    assert rect1.bottom - rect1.top > 0
    assert rect2.right - rect2.left > 0
    assert rect2.bottom - rect2.top > 0

    def get_four_corners(rect):
        return itertools.product((rect.left, rect.right), (rect.top, rect.bottom))

    return (any((is_in_rect(pos, rect2) for pos in get_four_corners(rect1))) or
            any((is_in_rect(pos, rect1) for pos in get_four_corners(rect2))))
