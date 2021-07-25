import json


def msg_to_bytes(msg):
    msg_str = json.dumps(msg)
    return (msg_str).encode("utf8") + b"\0"


def bytes_to_msg(data):
    return json.loads(data[:-1])


class MessageFormer:
    MSG_SEP = b"\x00"

    def __init__(self):
        self.__fragments = []
        self.__messages = []

    def add_data(self, data):
        if self.MSG_SEP in data:
            end_frag, *messages, begin_frag = data.split(self.MSG_SEP)
            self.__fragments.append(end_frag)
            msg = b"".join(self.__fragments)
            self.__messages.append(msg)
            self.__messages.extend(messages)
            self.__fragments = [begin_frag]
        else:
            self.__fragments.append(data)

    def has_msg(self):
        return bool(self.__messages)

    def pop_msg(self):
        if not self.__messages:
            raise RuntimeError
        msg = self.__messages[0] + self.MSG_SEP
        self.__messages = self.__messages[1:]
        return msg

    def reset(self):
        self.__fragments = []
        self.__messages = []
