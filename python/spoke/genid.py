import uuid as uuid_std

def uuid():
    return str(uuid_std.uuid4())

next_id = 0
def luid():
    global next_id
    id = next_id
    next_id += 1
    return str(next_id)

