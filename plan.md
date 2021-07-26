# TODOs

* Make everything more robust
    * Add spotty-spoke command for help with testing (repeatedly starts and stops a pubsub spoke server)
    * Be more disciplined about when to await, create task or just make synchronous calls
* Packaging
    * Add documentation
    * Test with older pythons and relax version requirements
    * Consider adding type annotations and test that runs mypy
* Remove timeout args from awaitables and use standard asyncio approach

# Old notes

## client/server rewrite

Separate into three layers

### connection layer (layer 1)

Maintains a TCP connection

Parameters for:
* host/port
* connection timeout
Callbacks for:
* on first connect
* on reconnect
* on disconnect
* on recv bytes
    * Callback that takes bytes object as arg
Methods for:
* send bytes

### message layer (layer 2)

Handles message packing/unpacking (JSON)

* Wrapper for layer 1
* Handles splitting messages by "\0"
* Handles parsing/dumping json

### pub/sub layer (layer 3)

Adds pub/sub and RPC functionality

* Sends control messages for subscribing/unsubscribing
* Maintains routing/callback table for subscriptions
* Resends subscriptions on reconnect

## Robustness

Three aspects to robustness

### Robust handling of disconnections

* Server detects when a client has disconnected and deletes client (and subscriptions) from memory
* Client detects when a connection is dropped/fails and will keep trying to reconnect

### Subscription synchronization

* Client should be the source of truth on its list of subscriptions
* Send full list to server upon connecting

### RCP failure recovery

* Caller should use a timeout
* Think about an ack message that is published when the callee receives the message to show it is there
    * Distinguish between a call nobody's listening to and a call that has an error when executed

## Support wildcard subscriptions w/ nested channels

* Of the form /foo/bar/buzz
* A `*` can be used to replace one identifier
* A `**` replaces any number of identifiers
* Eg: `/foo/*/buzz`, `/**/buzz`, and `/**` all match
* For now, ignore a `/` at beginning of channel path - in the future may allow "relative paths"
* Multiple slashes and trailing slashes are ignored
* Either wildcard must be the only thing at its level, otherwise it's treated as a normal character

## RPC

Implement remote procedure calls

Requirements

* Multiple clients should be able to make a request to the same channel all at once, and each client should get back its own response
* A client should be able to make multiple requests before getting any responses, and when it gets the responses it can tell which response goes with which request
* The algorithm used should be extendable to a multi-server configuration and be robust to topology changes at any time. As long as there still exists a route between the caller and callee, it should still work.

### Possible using only pubsub messages?

Caller

* Suppose caller is making a call to channel `/foo`
* Subscribe to `/foo/-rpc/#/<ID>/result`, where `<ID>` is a locally generated unique id
* Publish to `/foo/-rpc/#/<ID>/call`, return a future
* Handle response on `/foo/-rpc/#/<ID>/result` then unsubscribe

Callee

* Subscribe to `/foo/**/call`
* Reply on `/foo/**/result`

Issue, how to assign a unique id to each client?
Find if server handles it, but how can it work with multiple bridged servers?

Suppose a server + clients have a way of generating unique ids among themselves.  
When you merge two such networks how do you avoid collisions?  
If you potentially change some ids, how does an in-transit rpc arrive at the correct location?

How about something like NAT? When a server needs to route an rpc to another server it makes a new proxy rpc to the remote server, using its bridge client

How does server know it's an RPC?

OR

Just use uuid4 for the client ID and assume there are never collisions
