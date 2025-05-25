# election.py
import Pyro5.api
import threading

class ElectionManager:
    def __init__(self, peer, peers_uris, epoch):
        self.peer = peer
        self.peers_uris = peers_uris
        self.votes = 1  # Vota em si mesmo
        self.epoch = epoch + 1
        self.lock = threading.Lock()

    def start_election(self):
        print(f"[{self.peer.name}] Iniciando eleição da época {self.epoch}...")
        threads = []
        for uri in self.peers_uris:
            t = threading.Thread(target=self.request_vote, args=(uri,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        if self.votes > len(self.peers_uris) // 2:
            print(f"[{self.peer.name}] Eleito novo tracker!")
            return True
        else:
            print(f"[{self.peer.name}] Falha na eleição.")
            return False

    def request_vote(self, uri):
        try:
            peer = Pyro5.api.Proxy(uri)
            response = peer.vote_candidate(self.peer.name, self.epoch)
            if response:
                with self.lock:
                    self.votes += 1
        except:
            pass
