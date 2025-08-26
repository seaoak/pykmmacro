from dataclasses import dataclass
import dataclasses
import itertools
import random
import time
from typing import Any, Callable, Final, Generator, Iterable, Self

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

@dataclass(frozen=True)
class MyPosition:
    x: int
    y: int

    def __post_init__(self):
        pass

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __str__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def __iter__(self):
        yield self.x
        yield self.y

    def move(self, diff_x: int, diff_y: int) -> Self:
        # may be assertion error if diff_x or diff_x is negative
        return type(self)(self.x + diff_x, self.y + diff_y)

@dataclass(frozen=True)
class MyOffsetInRect(MyPosition):
    def __post_init__(self):
        super().__post_init__()
        assert self.x >= 0
        assert self.y >= 0

@dataclass(frozen=True)
class MyRect:
    # the order of fields follows CSS (Cascading Style Sheet)
    top: int
    right: int
    bottom: int
    left: int

    def __post_init__(self):
        assert self.top <= self.bottom
        assert self.left <= self.right

    @property
    def width(self):
        return self.right - self.left # may be zero

    @property
    def height(self):
        return self.bottom - self.top # may be zero

    @property
    def corners(self) -> Iterable[MyPosition]:
        tuples = itertools.product((self.left, self.right), (self.top, self.bottom))
        return (MyPosition(*t) for t in tuples)

    @classmethod
    def from_namedtuple(cls, d: Any) -> Self:
        return cls(top=d.top, right=d.right, bottom=d.bottom, left=d.left)

    def asdict(self):
        return dataclasses.asdict(self)

    def includes(self, pos: MyPosition) -> bool:
        assert self.right - self.left > 0
        assert self.bottom - self.top > 0
        x, y = pos.as_tuple()
        return self.left <= x and x < self.right and self.top <= y and y < self.bottom

    def is_intersect(self, other: Self) -> bool:
        assert self.right - self.left > 0
        assert self.bottom - self.top > 0
        assert other.right - other.left > 0
        assert other.bottom - other.top > 0

        return (any((other.includes(pos) for pos in self.corners)) or
                any((self.includes(pos) for pos in other.corners)))

def is_in_rect(pos: tuple[int, int], rect: Any) -> bool:
    return MyRect.from_namedtuple(rect).includes(MyPosition(*pos))

def is_rect_intersect(rect1: Any, rect2: Any) -> bool:
    return MyRect.from_namedtuple(rect1).is_intersect(MyRect.from_namedtuple(rect2))
