# main.py
import multiprocessing
import os
import time
from pathlib import Path
import Pyro5.api
import Pyro5.nameserver
from peer import Peer
from tracker import Tracker
from file_transfer import FileTransferService
from menu import exibir_menu

Pyro5.api.config.SERIALIZER = "serpent"  # serpent is default, but best to be explicit

PEERS = ["peer1", "peer2", "peer3", "peer4", "peer5"]

def start_nameserver():
    Pyro5.nameserver.start_ns_loop()

def start_peer(name, is_tracker=False):
    files_dir = f"./files/{name}"
    Path(files_dir).mkdir(parents=True, exist_ok=True)
    initial_files = os.listdir(files_dir)

    peer = None
    if is_tracker:
        peer = Tracker(name, initial_files)
    else:
        peer = Peer(name, initial_files)
    
    file_service = FileTransferService(files_dir)

    with Pyro5.api.Daemon() as daemon:
        ns = Pyro5.api.locate_ns()
        peer_uri = daemon.register(peer)
        file_uri = daemon.register(file_service)

        ns.register(name, peer_uri)
        ns.register(name + "_file", file_uri)

        if is_tracker:
            ns.register("Tracker_Atual", peer_uri)
        else:
            # Aguarda tracker aparecer
            while True:
                try:
                    tracker_uri = ns.lookup("Tracker_Atual")
                    peer.tracker_uri = tracker_uri
                    peer.register_with_tracker()
                    break
                except:
                    time.sleep(0.5)


        print(f"[{name}] Pronto.")
        daemon.requestLoop()

if __name__ == "__main__":
    ns_proc = multiprocessing.Process(target=start_nameserver)
    ns_proc.start()
    time.sleep(1)

    peer_procs = []
    for i, name in enumerate(PEERS):
        proc = multiprocessing.Process(target=start_peer, args=(name, i == 0))
        proc.start()
        peer_procs.append(proc)

    time.sleep(3)  # Espera todos registrarem
    ns = Pyro5.api.locate_ns()
    exibir_menu("peer2", ns.lookup("peer2"), ns)  # Exemplo: menu do peer2

    for p in peer_procs:
        p.terminate()
    ns_proc.terminate()
