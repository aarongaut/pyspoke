import spoke


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

    def __repr__(self):
        return f"Message(head={self.head}, body={self.body})"


class MessagePacker(spoke.conn.abc.AbstractPacker):
    def __init__(self):
        self.__json_packer = spoke.conn.pack.JsonPacker()

    def pack(self, msg):
        json_msg = {
            "head": msg.head,
            "body": msg.body,
        }
        return self.__json_packer.pack(json_msg)

    def unpack(self, data):
        self.__json_packer.unpack(data)

    def __iter__(self):
        return self

    def __next__(self):
        json_msg = next(self.__json_packer)
        if not isinstance(json_msg, dict):
            raise ValueError("json_msg is not a dict")
        head = json_msg.get("head", None)
        if not isinstance(head, dict):
            raise ValueError("head is not present or is not a dict")
        channel = head.get("channel", None)
        if not isinstance(channel, str):
            raise ValueError("channel is not present or is not a string")
        body = json_msg.get("body", None)
        return Message(body=body, **head)

    def reset(self):
        self.__json_packer.reset()
