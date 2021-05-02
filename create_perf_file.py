#!mitmdump -s

import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
import json

class SniffWebSocket:
    user_list = {}
    def __init__(self):
        pass

    # Websocket lifecycle
    def websocket_handshake(self, flow: mitmproxy.http.HTTPFlow):
        """
            Called when a client wants to establish a WebSocket connection. The
            WebSocket-specific headers can be manipulated to alter the
            handshake. The flow object is guaranteed to have a non-None request
            attribute.
        """

    def websocket_start(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has commenced.
        """

    def websocket_message(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            Called when a WebSocket message is received from the client or
            server. The most recent message will be flow.messages[-1]. The
            message is user-modifiable. Currently there are two types of
            messages, corresponding to the BINARY and TEXT frame types.
        """
        for flow_msg in flow.messages:
            packet = flow_msg.content
            # in future if needed to get registered user : RegisteredUsersResponse
            # req -  '5:4+::{"name":"RegisterUsersRequest","args":[{"roundID":18645}]}'
            if "ChallengeTable" in packet[:100]:
                print(len(self.user_list), " - TODO: decode the packet here: %r..." % packet)
                j = json.loads(packet.split(":::")[1])
                for arg in j["args"]:
                    for c in arg["coders"]:
                        self.user_list[(c["userName"])] = {"rating":c["userRating"], "score":c["totalPoints"]}    
                with open("perf.txt", "w") as f:
                    f.write(json.dumps(self.user_list))
            else:
                print("HALF::%r....." % packet[:200])

    def websocket_error(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has had an error.
        """

    def websocket_end(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has ended.
        """

addons = [
    SniffWebSocket()
]


