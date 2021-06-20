import json
def msg_to_bytes(channel, msg=None):
    full_msg = {
        "channel": channel,
        "payload": msg,
    }
    msg_str = json.dumps(full_msg)
    return (msg_str).encode("utf8") + b"\0"

def bytes_to_msg(msg_data):
    full_msg = json.loads(msg_data[:-1].decode("utf8"))
    channel = full_msg.get("channel", None)
    msg = full_msg.get("payload", None)
    return channel, msg

