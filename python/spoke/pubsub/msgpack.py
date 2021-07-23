import spoke
import json


def pack_msg(channel, payload=None):
    full_msg = {
        "channel": spoke.pubsub.route.canonical(channel),
        "payload": payload,
    }
    return full_msg


def unpack_msg(full_msg):
    channel = full_msg.get("channel", None)
    if not isinstance(channel, str):
        raise ValueError("channel is not a string")
    channel = spoke.pubsub.route.canonical(channel)
    payload = full_msg.get("payload", None)
    return channel, payload
