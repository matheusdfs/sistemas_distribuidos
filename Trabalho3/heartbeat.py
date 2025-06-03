# heartbeat.py
import threading
import time
import random
import Pyro5.api

PEERS = ["peer1", "peer2", "peer3", "peer4", "peer5"]

class HeartbeatManager:
    def __init__(self, tracker_uri):
        self.tracker_uri = tracker_uri
        self.running = True

        ns = Pyro5.api.locate_ns()
        self.peers_uris = []
        for peer in PEERS:
            try:
                self.peers_uris.append(ns.lookup(peer))
            except Pyro5.errors.NamingError:
                continue

    def start(self):
        thread = threading.Thread(target=self.send_heartbeat_loop)
        thread.daemon = True
        thread.start()

    def send_heartbeat_loop(self):
        while self.running:
            print("dalo")
            if random.random() < 0.5:
                print("[Heartbeat] Parando batimento cardíaco...")
                self.running = False
            for uri in self.peers_uris:
                try:
                    peer = Pyro5.api.Proxy(uri)
                    peer.receive_heartbeat()
                except:
                    continue
            time.sleep(0.1)
