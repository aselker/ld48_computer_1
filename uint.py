import math


class UintN:
    def __init__(self, number, n):
        self.n = n
        assert 0 <= number and number < 2 ** self.n
        self.number = number

    def bits(self):
        number = self.number
        bits = [None] * self.n
        for i in range(self.n):
            bits[self.n-1-i] = bool(number % 2)
            number = int(math.floor(number / 2))

        return bits

    def __add__(self, other):
        return (self.number + other.number) % 2 ** self.n


class Uint6(UintN):
    def __init__(self, number):
        super().__init__(number, 6)
