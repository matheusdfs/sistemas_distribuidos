# peer.py
import os
import time
import random
import base64
import Pyro5.api
import threading

from pathlib import Path
from Pyro5.serializers import serpent

@Pyro5.api.expose
class Peer:
    def __init__(self, name, is_electing, epoch=0, is_tracker=False):
        files_dir = f"./files/{name}"
        Path(files_dir).mkdir(parents=True, exist_ok=True)
        files = os.listdir(files_dir)

        self.name = name
        self.files = set(files)
        self.epoch = epoch
        self.uri = None
        self.tracker_uri = None
        self.heartbeat_timer = None
        self.alive = True
        self.epoch = epoch
        self.ultimo_voto = -1
        self.is_electing = is_electing

        daemon =  Pyro5.api.Daemon()
        ns = Pyro5.api.locate_ns()
        self.uri = daemon.register(self)

        if is_tracker:
            print("registrado tracker atual")
            ns.register(f"Tracker_Atual", self.uri)
        else:
            ns.register(name, self.uri)

        # Aguarda tracker aparecer
        if not is_tracker:
            while True:
                try:
                    print(f"[{name}] Buscando Tracker_Atual")
                    self.tracker_uri = ns.lookup(f"Tracker_Atual")
                    self.register_with_tracker()
                    break
                except:
                    time.sleep(0.5)

        print(f"[{name}] Pronto.")
        daemon.requestLoop()

    def list_files(self):
        return list(self.files)

    def has_file(self, filename):
        return filename in self.files

    def add_file(self, filename):
        self.files.add(filename)
        print(f"[{self.name}] Arquivo '{filename}' adicionado.")
        if self.tracker_uri:
            self.notify_tracker()

    def remove_file(self, filename):
        self.files.discard(filename)
        print(f"[{self.name}] Arquivo '{filename}' removido.")
        if self.tracker_uri:
            self.notify_tracker()

    def notify_tracker(self):
        try:
            tracker = Pyro5.api.Proxy(self.tracker_uri)
            tracker.update_index(self.name, list(self.files))
            print(f"[{self.name}] Tracker notificado sobre arquivos.")
        except:
            print(f"[{self.name}] Falha ao notificar tracker.")

    def receive_heartbeat(self):
        print(f"[{self.name}] Recebendo heartbeat do tracker.")
        self.reset_timer()

    def reset_timer(self):
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.heartbeat_timer = threading.Timer(
            timeout := (0.15 + (0.15 * random.random()) % 0.15),
            self.tracker_failed
        )
        self.heartbeat_timer.start()

    def tracker_failed(self):
        atraso = random.uniform(0.05, 0.2)
        time.sleep(atraso)
        print(f"[{self.name}] Tracker inativo. Iniciando eleição...")
        self.iniciar_eleicao()

    def register_with_tracker(self):
        try:
            tracker = Pyro5.api.Proxy(self.tracker_uri)
            tracker.register_files(self.name, list(self.files))
            print(f"[{self.name}] Arquivos registrados no tracker.")
        except Exception as e:
            print(f"[{self.name}] Erro ao registrar arquivos: {e}")

    def get_file(self, filename):
        try:
            with open(f"./files/{self.name}/{filename}", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def save_file(self, filename, content):
        content = serpent.tobytes(content)
        with open(f"./files/{self.name}/{filename}", "wb") as f:
            f.write(base64.b64decode(content))
        print(f"[{self.name}] Arquivo '{filename}' salvo.")

    def vote_candidate(self, epoch):
        if epoch > self.ultimo_voto:
            self.ultimo_voto = epoch
            self.epoch = epoch
            return True
        else:
            print(f"[{self.name}] Já votei na época {self.ultimo_voto}, ignorando.")
            return False
    
    def iniciar_eleicao(self):
        if not self.is_electing.value:
            self.is_electing.value = True
            print(f"[{self.name}] Eleições desativadas, iniciando eleição para peer.")
        else:
            return

        from election import ElectionManager
        ns = Pyro5.api.locate_ns()
        
        # Obtém URIs de todos os peers, menos ele mesmo
        peer_uris = []
        for name, uri in ns.list(prefix="peer").items():
            if name != self.name:
                peer_uris.append(uri)

        self.election = ElectionManager(self, peer_uris, self.epoch)
        sucesso = self.election.start_election()

        if sucesso:
            self.epoch += 1
            ns.register(f"Tracker_Atual", self.uri)
            print(f"[{self.name}] Novo tracker registrado como Tracker_Atual.")
            # Notificar os outros peers
            for uri in peer_uris:
                try:
                    p = Pyro5.api.Proxy(uri)
                    p.atualizar_tracker(ns.lookup(f"Tracker_Atual"))
                except:
                    continue

        print(f"[{self.name}] Eleições ativadas novamente.")
        self.is_electing.value = False

    def atualizar_tracker(self, tracker_uri):
        self.tracker_uri = tracker_uri
        print(f"[{self.name}] Tracker atualizado para {tracker_uri}.")
        self.register_with_tracker()
        self.reset_timer()



