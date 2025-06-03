# main.py
import multiprocessing
import os
import time
from pathlib import Path
import Pyro5.api
import Pyro5.nameserver
from peer import Peer
from tracker import Tracker
from menu import exibir_menu
from multiprocessing import Manager

Pyro5.api.config.SERIALIZER = "serpent"  # serpent is default, but best to be explicit

PEERS = ["peer1", "peer2", "peer3", "peer4", "peer5"]

def start_nameserver():
    Pyro5.nameserver.start_ns_loop()

def start_peer(name, is_electing, epoch):
    print(f"Iniciando {name}...")
    if name == "peer1":
        Tracker(name, is_electing, epoch)
    else:
        Peer(name, is_electing, epoch)

if __name__ == "__main__":
    manager = Manager()
    is_electing = manager.Value('b', True)  # 'b' = booleano
    is_electing.value = False

    ns_proc = multiprocessing.Process(target=start_nameserver)
    ns_proc.start()
    time.sleep(1)

    peer_procs = []
    for i, name in enumerate(PEERS):
        proc = multiprocessing.Process(target=start_peer, args=(name, is_electing, 0))
        proc.start()
        peer_procs.append(proc)

    time.sleep(3)  # Espera todos registrarem
    ns = Pyro5.api.locate_ns()
    exibir_menu("peer2", ns.lookup("peer2"), ns)  # Exemplo: menu do peer2

    for p in peer_procs:
        p.terminate()
    ns_proc.terminate()
