# peer.py
import random
import Pyro5.api
import threading
import base64

from Pyro5.serializers import serpent

@Pyro5.api.expose
class Peer:
    def __init__(self, name, files, epoch=0):
        self.name = name
        self.files = set(files)
        self.epoch = epoch
        self.tracker_uri = None
        self.heartbeat_timer = None
        self.alive = True

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
        print(f"[{self.name}] Tracker inativo. Iniciando eleição...")
        # Aqui chamará ElectionManager futuramente

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


