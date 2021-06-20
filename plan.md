# TODOs

Include channel as a subscribe callback arg

## Support wildcard subscriptions w/ nested channels

* Of the form /foo/bar/buzz
* A `*` can be used to replace one identifier
* A `**` replaces any number of identifiers
* Eg: `/foo/*/buzz`, `/**/buzz`, and `/**` all match
* For now, ignore a `/` at beginning of channel path - in the future may allow "relative paths"
* Multiple slashes and trailing slashes are ignored
* Either wildcard must be the only thing at its level

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
* Publish to `/foo/-rpc/#/<ID>`, return a future
* Handle response on `/foo/-rpc/#/<ID>/result` then unsubscribe

Callee

* Subscribe to `/foo/**`
* Reply on `channel + /result` where channel is whatever channel the message came in on

Issue, how to assign a unique id to each client?
Find if server handles it, but how can it work with multiple bridged servers?

Suppose a server + clients have a way of generating unique ids among themselves.  
When you merge two such networks how do you avoid collisions?  
If you potentially change some ids, how does an in-transit rpc arrive at the correct location?

How about something like NAT? When a server needs to route an rpc to another server it makes a new proxy rpc to the remote server, using its bridge client

How does server know it's an RPC?

OR

Just use uuid4 for the client ID and assume there are never collisions
