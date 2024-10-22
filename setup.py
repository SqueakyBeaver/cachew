import json


def calcVal(key: int) -> str:
    legend = "abcdefghijklmnopqrstuvwxyz"

    val = ""
    # RIP, no do-while loop
    while True:
        val += legend[key % 26]
        key = key // 26

        if key == 0:
            break

    return val


# Serialize into json
# {
#   0: "a",
#   ...
#   012: "abc",
# }
cache_small = {}
cache_large = {}

# 2^8
for i in range(0, 256):
    cache_small[i] = calcVal(i)

with open("inputs/small.json", mode="w+") as file:
    json.dump(cache_small, file)

# 2^18, an arbitrary number
for i in range(0, 262144):
    cache_large[i] = calcVal(i)

with open("inputs/large.json", mode="w+") as file:
    json.dump(cache_large, file)
