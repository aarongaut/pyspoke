def tokenize(channel):
    tokens = [t for t in channel.split("/") if t]
    change = True
    # In runs of * and ** tokens, all the * tokens should come first to simplify matching
    is_wc = [t in ("*", "**") for t in tokens]
    edges = [i + 1 for i, (l, r) in enumerate(zip(is_wc[:-1], is_wc[1:])) if l != r]
    run_idxs = [0] + edges + [len(tokens)]
    runs = [tokens[start:end] for start, end in zip(run_idxs[:-1], run_idxs[1:])]
    for run in runs:
        if "**" not in run:
            continue
        wc1_count = sum([x == "*" for x in run])
        run.clear()
        run.extend(["*"] * wc1_count)
        run.append("**")
    return tuple(sum(runs, []))


def canonical(channel):
    return Route(tokenize(channel), None).channel()


class Route:
    def __init__(self, tokens, destination=None):
        if isinstance(tokens, str):
            raise ValueError("tokens should not be a string")
        self.tokens = tokens
        self.destination = destination

    def __eq__(self, other):
        return self.tokens == other.tokens

    def __hash__(self):
        return hash(self.tokens)

    def test(self, tokens):
        if isinstance(tokens, str):
            raise ValueError("tokens should not be a string")
        stack = [(0, 0)]
        while stack:
            ci, ri = stack.pop()
            if ci >= len(tokens) and ri >= len(self.tokens):
                return True
            if ri >= len(self.tokens):
                continue
            rt = self.tokens[ri]
            if ri == len(self.tokens) - 1 and rt == "**":
                return True
            if ci >= len(tokens):
                continue
            ct = tokens[ci]
            if rt == "*" or rt == ct:
                stack.append((ci + 1, ri + 1))
                continue
            if rt == "**":
                lrt = self.tokens[ri + 1]
                for lci, lct in enumerate(tokens[ci:]):
                    if lrt == lct:
                        stack.append((lci + ci, ri + 1))
                continue
        return False

    def channel(self):
        return "/".join(self.tokens)


class RoutingTable:
    def __init__(self):
        self.routes = set()

    def add_rule(self, channel, destination=None):
        tokens = tokenize(channel)
        route = Route(tokens, destination)
        self.routes.add(route)
        return route

    def remove_rule(self, channel):
        tokens = tokenize(channel)
        route = Route(tokens, None)
        if route in self.routes:
            self.routes.remove(route)
        return route

    def get_destinations(self, channel):
        tokens = tokenize(channel)
        return [e.destination for e in self.routes if e.test(tokens)]
