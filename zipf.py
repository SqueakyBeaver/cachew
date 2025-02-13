import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import zeta
import itertools
import timeit


def zipf(num_unique: int, shape: float, request_count: int):
    norm_const = 1 / sum((i**shape for i in range(1, num_unique + 1)))

    def gen_elements():
        total = 0
        for i in range(num_unique):
            freq = norm_const * ((i + 1) ** shape)
            cnt = round(freq * request_count)
            total += cnt
            print(i, cnt)
            yield from itertools.repeat(i, cnt)

        if total < request_count:
            yield from itertools.repeat(0, request_count - total)

    ret = list(gen_elements())

    random.shuffle(ret)
    return ret


z = zipf(4096 * 2, -.75, 10000)
# print(timeit.timeit("zipf(256, -.75, 10000)", number=4, globals=globals() | locals()))
k = np.arange(1, max(z) + 1)
cnt = np.bincount(z)
plt.bar(k, cnt[1:])
plt.show()

# a = 1.2
# n = 10000
# s = np.random.default_rng().zipf(a, n)
# # z = zipf()
# count = np.bincount(s)
# k = np.arange(1, s.max() + 1)
# plt.bar(k, count[1:], alpha=0.5, label="sample count")
# plt.plot(k, n * (k**-a) / zeta(a), "k.-", alpha=0.5, label="expected count")
# plt.semilogy()
# plt.grid(alpha=0.4)
# plt.legend()
# plt.title(f"Zipf sample, a={a}, size={n}")
# plt.show()
