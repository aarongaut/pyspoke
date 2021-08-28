import spoke


try:
    spoke.call("junk", None, timeout=2)
except TimeoutError:
    print("Got expected TimeoutError")
else:
    raise TestFailure("Didn't get a TimeoutError")
