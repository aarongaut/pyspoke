import random
import spoke


def slice_and_dice(string, seed=None):
    random.seed(seed)
    cuts = random.randrange(1, 6)
    parts = [string]
    for _ in range(cuts):
        part_idx = random.randrange(0, len(parts))
        part = parts[part_idx]
        byte_idx = random.randrange(0, len(part) + 1)
        parts = (
            parts[:part_idx]
            + [part[:byte_idx], part[byte_idx:]]
            + parts[part_idx + 1 :]
        )
    return parts


cases = [
    {
        "input": b"hello\x00world\x00",
        "expected": [b"hello", b"world"],
    },
    {
        "input": b"hello\x00\x00world\x00junk",
        "expected": [b"hello", b"", b"world"],
    },
]


class TestFailure(AssertionError):
    pass


reps = 100
for case in cases:
    random.seed(case["input"])
    seeds = [str(random.random()) for _ in range(reps)]
    for seed in seeds:
        fragments = slice_and_dice(case["input"], seed)
        former = spoke.conn.pack.DelimitedBytePacker()
        for fragment in fragments:
            former.unpack(fragment)
        messages = []
        for msg in former:
            messages.append(msg)
        if messages != case["expected"]:
            msg = 'Unexpected result {} for input {} on seed "{}", case {}.'
            raise TestFailure(msg.format(messages, fragments, seed, case))

print("All {} cases passed".format(len(cases) * reps))
