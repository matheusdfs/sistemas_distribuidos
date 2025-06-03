# tracker.py
import Pyro5.api

from peer import Peer
from heartbeat import HeartbeatManager

@Pyro5.api.expose
class Tracker(Peer):
    def __init__(self, name, is_electing, epoch=0):
        super().__init__(name, is_electing, epoch, is_tracker=True)
        self.index = {}  # {filename: set(peer_names)}
        self.heartbeat = HeartbeatManager(self.tracker_uri)
        self.heartbeat.start()

    def register_files(self, peer_name, file_list):
        for file in file_list:
            self.index.setdefault(file, set()).add(peer_name)
        print(f"[{self.name}] Arquivos registrados de {peer_name}.")

    def update_index(self, peer_name, file_list):
        # Remove peer de todos os arquivos
        for file_set in self.index.values():
            file_set.discard(peer_name)

        # Adiciona de volta os arquivos atuais
        for file in file_list:
            self.index.setdefault(file, set()).add(peer_name)
        print(f"[{self.name}] Índice atualizado com arquivos de {peer_name}.")

    def search_file(self, filename):
        peers = list(self.index.get(filename, []))
        print(f"[{self.name}] Peers com '{filename}': {peers}")
        return peers
