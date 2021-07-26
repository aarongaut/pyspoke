def server():
    import asyncio
    import spoke

    server = spoke.pubsub.server.Server()

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        pass
    return 0


def echo():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-path", "-o", help="File to write to in addition to printing"
    )
    parser.add_argument(
        "--first",
        "-f",
        action="store_true",
        help="Exit after echoing the first received message",
    )
    parser.add_argument(
        "--label", "-l", help="Label to include at beginning of each output"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print the full message head and body",
    )
    parser.add_argument("channel", nargs="*", default=["**"])
    args = parser.parse_args()

    import asyncio
    import spoke
    import signal

    if args.output_path:
        ostream = open(args.output_path, "w")
    else:
        ostream = None

    async def echo(msg):
        if args.verbose:
            msg_text = str(msg.pack())
        else:
            msg_text = "{}: {}".format(msg.channel, msg.body)
        if args.label:
            output = "[{}] {}\n".format(args.label, msg_text)
        else:
            output = msg_text + "\n"
        print(output, end="")
        if ostream:
            ostream.write(output)
        if args.first:
            signal.raise_signal(signal.SIGTERM)

    async def main():
        client = spoke.pubsub.client.Client()
        await client.run()
        await asyncio.gather(
            *[client.subscribe(x, echo, bounce=False) for x in args.channel]
        )
        await spoke.wait()
        if ostream:
            ostream.close()

    asyncio.run(main())
    return 0


def call():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("channel")
    parser.add_argument("body", nargs="?", default=None)
    parser.add_argument("-t", "--timeout", type=float, default=None)
    args = parser.parse_args()

    import json
    import spoke

    if args.body is None:
        body = args.body
    else:
        body = json.loads(args.body)

    try:
        print(spoke.call(args.channel, body, timeout=args.timeout))
    except TimeoutError:
        print("Timeout")
        return 1
    except spoke.pubsub.error.RemoteCallError as e:
        msg = "Error: {}"
        print(msg.format(e))
        return 1
    return 0


def publish():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("channel")
    parser.add_argument("body", nargs="?", default=None)
    parser.add_argument("--persist", "-p", action="store_true")
    parser.add_argument("--timeout", "-t", type=float)
    args = parser.parse_args()

    import json
    import spoke

    if args.body is None:
        body = args.body
    else:
        body = json.loads(args.body)

    spoke.publish(args.channel, body, timeout=args.timeout, persist=args.persist)
    return 0


def bridge():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port1", type=int, default=7181)
    parser.add_argument("--host1", default="127.0.0.1")
    parser.add_argument("--port2", type=int, default=7181)
    parser.add_argument("--host2", default="127.0.0.1")
    args = parser.parse_args()

    import asyncio
    import spoke

    if args.port1 == args.port2 and args.host1 == args.host2:
        print("The given arguments will bridge the server to itself. Aborting.")
        return 1

    def mirror(other):
        async def _inner(msg):
            if msg.channel.startswith("-control/"):
                return
            msg.head["bounce"] = False
            await other.publish(body=msg.body, **msg.head)

        return _inner

    async def main():
        client1 = spoke.pubsub.client.Client(port=args.port1, host=args.host1)
        await client1.run()
        client2 = spoke.pubsub.client.Client(port=args.port2, host=args.host2)
        await client2.run()
        await client1.subscribe("**", mirror(client2))
        await client2.subscribe("**", mirror(client1))
        await spoke.wait()

    asyncio.run(main())
    return 0
