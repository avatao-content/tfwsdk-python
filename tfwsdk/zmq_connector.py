from zmq.eventloop.zmqstream import ZMQStream
import zmq
import json
import os

class ZMQDownlinkConnector:
    def __init__(self, connect_addr):
        self._zmq_sub_socket = zmq.Context.instance().socket(zmq.SUB)
        self._zmq_sub_socket.setsockopt(zmq.RCVHWM, 0)
        self._zmq_sub_socket.connect(connect_addr)
        self._zmq_sub_stream = ZMQStream(self._zmq_sub_socket)
        self._zmq_sub_socket.setsockopt_string(zmq.SUBSCRIBE, '') # Subscribing to every message

    def register_callback(self, callback):
        self._zmq_sub_stream.on_recv(callback)

    def close(self):
        self._zmq_sub_stream.close()

class ZMQUplinkConnector:
    def __init__(self, connect_addr):
        self._zmq_push_socket = zmq.Context.instance().socket(zmq.PUSH)
        self._zmq_push_socket.setsockopt(zmq.SNDHWM, 0)
        self._zmq_push_socket.connect(connect_addr)

    def send_message(self, message):
        message['scope'] = 'zmq'
        zmq_message = (message['key'].encode(), json.dumps(message, sort_keys=True).encode())
        self._zmq_push_socket.send_multipart(zmq_message)

    def close(self):
        self._zmq_push_socket.close()

class ZMQConnector(ZMQDownlinkConnector, ZMQUplinkConnector):
    def __init__(self):
        self.downlink_bind_addr = f'tcp://localhost:{os.getenv("TFW_PUB_PORT", "7654")}'
        self.uplink_bind_addr = f'tcp://localhost:{os.getenv("TFW_PULL_PORT", "8765")}'
        ZMQDownlinkConnector.__init__(self, self.downlink_bind_addr)
        ZMQUplinkConnector.__init__(self, self.uplink_bind_addr)

    def close(self):
        ZMQDownlinkConnector.close(self)
        ZMQUplinkConnector.close(self)