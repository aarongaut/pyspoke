import spoke

class TestFailure(AssertionError):
    pass

try:
    spoke.simple.publish("foo", None, timeout=0.5)
except TimeoutError:
    print("Got expected TimeoutError")
else:
    raise TestFailure("Didn't get a TimeoutError")


