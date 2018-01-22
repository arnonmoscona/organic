"""
Common test mixin for random numbers
"""
import random


class RandomMixin:
    def random_natural(self, max_value=10000):
        return int(random.random() * max_value) + 1
