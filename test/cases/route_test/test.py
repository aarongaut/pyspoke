from spoke.pubsub.route import Route, tokenize

class TestFailure(AssertionError):
    pass

cases = [
    {
        "rule": "foo",
        "channel": "foo",
        "expected": True,
    },
    {
        "rule": "foo",
        "channel": "bar",
        "expected": False,
    },
    {
        "rule": "foo/bar",
        "channel": "foo/bar",
        "expected": True,
    },
    {
        "rule": "foo/bar",
        "channel": "foo/foo",
        "expected": False,
    },
    {
        "rule": "foo/*",
        "channel": "foo/bar",
        "expected": True,
    },
    {
        "rule": "*/bar",
        "channel": "foo/bar",
        "expected": True,
    },
    {
        "rule": "bar/*",
        "channel": "foo/bar",
        "expected": False,
    },
    {
        "rule": "*/foo",
        "channel": "foo/bar",
        "expected": False,
    },
    {
        "rule": "foo/foo/foo",
        "channel": "foo/foo",
        "expected": False,
    },
    {
        "rule": "**",
        "channel": "",
        "expected": True,
    },
    {
        "rule": "**",
        "channel": "foo",
        "expected": True,
    },
    {
        "rule": "**",
        "channel": "foo/bar/qux",
        "expected": True,
    },
    {
        "rule": "**/qux",
        "channel": "foo/bar/qux",
        "expected": True,
    },
    {
        "rule": "**/bar",
        "channel": "foo/bar/qux",
        "expected": False,
    },
    {
        "rule": "*/**",
        "channel": "",
        "expected": False,
    },
    {
        "rule": "*/**",
        "channel": "foo",
        "expected": True,
    },
    {
        "rule": "*/**/*",
        "channel": "foo/bar",
        "expected": True,
    },
    {
        "rule": "*/**/*",
        "channel": "foo/bar/qux",
        "expected": True,
    },
    {
        "rule": "*/**/*",
        "channel": "foo",
        "expected": False,
    },
    {
        "rule": "foo/**",
        "channel": "foo/asdf/qwer",
        "expected": True,
    },
    {
        "rule": "foo/**/bar",
        "channel": "foo/asdf/qwer/qux/bar",
        "expected": True,
    },
    {
        "rule": "foo/**/bar",
        "channel": "foo/asdf/qwer/bar/qux",
        "expected": False,
    },
    {
        "rule": "*asdf",
        "channel": "*",
        "expected": False,
    },
    {
        "rule": "*",
        "channel": "*asdf",
        "expected": True,
    },
    {
        "rule": "*asdf",
        "channel": "*asdf",
        "expected": True,
    },
    {
        "rule": "**/foo/**",
        "channel": "a/b/c/foo/d/e/f",
        "expected": True,
    },
    {
        "rule": "**/foo/**/bar/**/qux/**",
        "channel": "a/b/c/foo/d/e/f/bar/g/h/i/qux/j/k/l",
        "expected": True,
    },
    {
        "rule": "**/foo/**/bar/**/qux/**",
        "channel": "a/b/c/foo/d/e/f/br/g/h/i/qux/j/k/l",
        "expected": False,
    },
    {
        "rule": "foo/*/**/bar",
        "channel": "foo/bar",
        "expected": False,
    },
    {
        "rule": "foo/*/**/bar",
        "channel": "foo/qux/bar",
        "expected": True,
    },
    {
        "rule": "foo/*/**/bar",
        "channel": "foo/qux/asdf/qer/bar",
        "expected": True,
    },
]

for case in cases:
    rule = case["rule"]
    channel = case["channel"]
    expected = case["expected"]
    entry = Route(tokenize(rule), None)
    result = entry.test(tokenize(channel))
    if result != expected:
        msg = "Failed case {} - expected {}, got {}".format(case, expected, result)
        raise TestFailure(msg)

print("All {} cases passed".format(len(cases)))

