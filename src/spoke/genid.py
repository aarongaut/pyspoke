import uuid as uuid_std


def uuid():
    "Generate a universally unique string id"
    return str(uuid_std.uuid4())


_next_id = 0


def luid():
    "Generate a unique string id local to this process"
    global _next_id
    id = _next_id
    _next_id += 1
    return hex(id)[2:]
