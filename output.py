import csv

# data = [["Cache Size", "LRU Misses", "LFU Misses", "DRRIP Misses"], [128, 23, 8, 9]]


def output(fname: str, data: list[list]):
    """
    Output data to a given filename
    Data should be in the form of a 2d list of rows and columns
    """
    with open(f"data/{fname}.csv", "w+") as out_file:
        writer = csv.writer(
            out_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        writer.writerows(data)


# output("cache_size", data)
