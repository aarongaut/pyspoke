import spoke
import json


class Message:
    def __init__(self, channel, body, **head):
        self.head = head.copy()
        self.channel = channel
        self.body = body

    @property
    def channel(self):
        return self.head["channel"]

    @channel.setter
    def channel(self, value):
        if not isinstance(value, str):
            raise ValueError("channel is not a string")
        self.head["channel"] = spoke.pubsub.route.canonical(value)

    @staticmethod
    def unpack(json_msg):
        if not isinstance(json_msg, dict):
            raise ValueError("json_msg is not a dict")
        head = json_msg.get("head", None)
        if not isinstance(head, dict):
            raise ValueError("head is not preset or is not a dict")
        channel = head.get("channel", None)
        if not isinstance(channel, str):
            raise ValueError("channel is not preset or is not a string")
        body = json_msg.get("body", None)
        return Message(body=body, **head)

    def pack(self):
        json_msg = {
            "head": self.head,
            "body": self.body,
        }
        return json_msg
