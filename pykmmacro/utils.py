import itertools
import random
import time

#=============================================================================
# Constants

_DELAY_A_MOMENT = 0.1

#=============================================================================
# Exception

class MyFailAlways(Exception):
    pass

#=============================================================================
# Private functions

#=============================================================================
# Public functions

def my_fail_always():
    raise MyFailAlways()

def my_assert_eq(l, r, *rest):
    assert l == r, (l, r, *rest)

def my_unique(seq, *, key_func=lambda x: x):
    """
    Remove duplicated items in a sequence.
    If `key_func` is specified, the value of `key_func(item)` is used to distinguish an item from another item.
    """
    is_dedup = dict()
    def generate_result():
        for value in seq:
            key = key_func(value)
            if key in is_dedup:
                continue
            is_dedup[key] = True
            yield value
    return generate_result()

def my_random():
    """
    use the average as *approximate* Gaussian random value
    https://k11i.biz/blog/2016/11/05/approximate-gaussian-rng/
    """
    num = 100 # with no foundation
    acc = 0
    for _ in range(num):
        acc += random.random()
    return acc / num

def my_sleep(period_sec):
    time.sleep(period_sec)

def my_sleep_with_random(period_sec, /, *, variation_ratio=0.4):
    variation = period_sec * variation_ratio # may be zero
    period = (period_sec - variation / 2) + variation * my_random()
    my_sleep(period)

def my_sleep_a_moment(period_sec=_DELAY_A_MOMENT, /):
    my_sleep_with_random(period_sec, variation_ratio=0.2)

def my_get_timestamp_ms() -> int:
    return time.time_ns() // (1000 * 1000)

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
