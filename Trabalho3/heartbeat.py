# heartbeat.py
import threading
import time
import Pyro5.api

class HeartbeatManager:
    def __init__(self, tracker_uri, peers_uris):
        self.tracker_uri = tracker_uri
        self.peers_uris = peers_uris
        self.running = True

    def start(self):
        thread = threading.Thread(target=self.send_heartbeat_loop)
        thread.daemon = True
        thread.start()

    def send_heartbeat_loop(self):
        while self.running:
            for uri in self.peers_uris:
                try:
                    peer = Pyro5.api.Proxy(uri)
                    peer.receive_heartbeat()
                except:
                    continue
            time.sleep(0.1)
