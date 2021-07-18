import spoke
import json

def msg_to_bytes(channel, msg=None):
    full_msg = {
        "channel": channel,
        "payload": msg,
    }
    return spoke.message.serialize.msg_to_bytes(full_msg)

def bytes_to_msg(msg_data):
    full_msg = spoke.message.serialize.bytes_to_msg(msg_data)
    channel = full_msg.get("channel", None)
    msg = full_msg.get("payload", None)
    return channel, msg
