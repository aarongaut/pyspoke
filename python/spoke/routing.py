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


class Entry:
    def __init__(self, tokens, sub, sub_id=None):
        self.tokens = tokens
        self.sub = sub
        self.sub_id = sub_id or sub

    def __eq__(self, other):
        return self.tokens == other.tokens and self.sub_id == other.sub_id

    def __hash__(self):
        return hash((hash(self.tokens) * 73) ^ (hash(self.sub_id) * 71))

    def test(self, tokens):
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

class SubscriberTable:
    def __init__(self):
        self.entries = set()

    def add_rule(self, channel, sub, sub_id=None):
        tokens = tokenize(channel)
        entry = Entry(tokens, sub, sub_id)
        self.entries.add(entry)

    def remove_rule(self, channel, sub_id):
        tokens = tokenize(channel)
        entry = Entry(tokens, None, sub_id)
        if entry in self.entries:
            self.entries.remove(entry)

    def remove_sub(self, sub_id):
        condemned = []
        for entry in self.entries:
            if entry.sub_id == sub_id:
                condemned.append(entry)
        for x in condemned:
            self.entries.remove(x)

    def get_subs(self, channel):
        tokens = tokenize(channel)
        subs = set()
        for entry in self.entries:
            if entry.sub in subs:
                continue
            if entry.test(tokens):
                subs.add(entry.sub)
        return list(subs)
