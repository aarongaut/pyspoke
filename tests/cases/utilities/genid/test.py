import spoke

count = 10000


def scope_luids():
    print("Generating {} luids".format(count))
    luids = [spoke.genid.luid() for _ in range(count)]
    tokens = luids[:5] + ["..."] + luids[-5:]
    print("Here's a sample: {}".format(" ".join(tokens)))
    assert len(set(luids)) == count
    print("All unique")


scope_luids()


def scope_uuids():
    print("\nGenerating {} uuids".format(count))
    uuids = [spoke.genid.uuid() for _ in range(count)]
    tokens = uuids[:5] + ["..."] + uuids[-5:]
    print("Here's a sample: {}".format(" ".join(tokens)))
    assert len(set(uuids)) == count
    print("All unique")


scope_uuids()
