import random
import time

#=============================================================================
# Constants

_DELAY_A_MOMENT = 0.2

#=============================================================================
# Private functions

#=============================================================================
# Public functions

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
