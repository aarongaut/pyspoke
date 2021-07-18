from spoke.pubsub.route import tokenize

class TestFailure(AssertionError):
    pass

cases = [
    {
        "channel": "asdf",
        "expected": ("asdf",),
    },
    {
        "channel": "/asdf",
        "expected": ("asdf",),
    },
    {
        "channel": "/",
        "expected": (),
    },
    {
        "channel": "",
        "expected": (),
    },
    {
        "channel": "*",
        "expected": ("*",),
    },
    {
        "channel": "**",
        "expected": ("**",),
    },
    {
        "channel": "foo/bar",
        "expected": ("foo", "bar"),
    },
    {
        "channel": "*foo",
        "expected": ("*foo",),
    },
    {
        "channel": "foo*",
        "expected": ("foo*",),
    },
    {
        "channel": "foo/bar/buzz",
        "expected": ("foo", "bar", "buzz"),
    },
    {
        "channel": "foo/*/bar",
        "expected": ("foo", "*", "bar"),
    },
    {
        "channel": "foo/**/bar",
        "expected": ("foo", "**", "bar"),
    },
    {
        "channel": "foo/**/*/bar",
        "expected": ("foo", "*", "**", "bar"),
    },
    {
        "channel": "foo/**/*/**/bar",
        "expected": ("foo", "*", "**", "bar"),
    },
    {
        "channel": "foo/**/**/**/bar",
        "expected": ("foo", "**", "bar"),
    },
    {
        "channel": "foo/*/**/**/**/*/bar",
        "expected": ("foo", "*", "*", "**", "bar"),
    },
    {
        "channel": "*/foo/*/**/**/**/*/bar",
        "expected": ("*", "foo", "*", "*", "**", "bar"),
    },
]

for case in cases:
    channel = case["channel"]
    expected = case["expected"]
    result = tokenize(channel)
    if result != expected:
        msg = "Expected {}, got {}".format(expected, result)
        raise TestFailure(msg)

print("All {} cases passed".format(len(cases)))

