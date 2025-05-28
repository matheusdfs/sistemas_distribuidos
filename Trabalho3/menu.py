# menu.py
import Pyro5.api
from Pyro5.serializers import serpent

def exibir_menu(peer_name, peer_uri, ns):
    peer = Pyro5.api.Proxy(peer_uri)
    while True:
        print(f"\n--- MENU {peer_name} ---")
        print("1. Listar meus arquivos")
        print("2. Adicionar arquivo")
        print("3. Remover arquivo")
        print("4. Buscar arquivo")
        print("5. Baixar arquivo")
        print("6. Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            print("Arquivos locais:", peer.list_files())
        elif opcao == "2":
            nome = input("Nome do arquivo a adicionar: ")
            peer.add_file(nome)
        elif opcao == "3":
            nome = input("Nome do arquivo a remover: ")
            peer.remove_file(nome)
        elif opcao == "4":
            nome = input("Arquivo a buscar: ")
            tracker_name = ns.lookup("Tracker_Atual")
            tracker = Pyro5.api.Proxy(tracker_name)
            donos = tracker.search_file(nome)
            print(f"Peers com '{nome}':", donos)
        elif opcao == "5":
            nome = input("Arquivo a baixar: ")
            tracker_name = ns.lookup("Tracker_Atual")
            tracker = Pyro5.api.Proxy(tracker_name)
            donos = tracker.search_file(nome)
            if not donos:
                print("Arquivo não encontrado.")
                continue
            destino = donos[0]
            peer_remoto = Pyro5.api.Proxy(ns.lookup(destino + "_file"))
            conteudo = peer_remoto.get_file(nome)
            import base64
            conteudo_bytes = base64.b64decode(conteudo["data"].encode("utf-8"))
            print(conteudo_bytes)
            if conteudo_bytes:
                peer_file = Pyro5.api.Proxy(ns.lookup(peer_name + "_file"))
                # Pass only the bytes to save_file, not the whole dict
                print(type(conteudo_bytes))
                print(type(nome))
                peer_file.save_file(nome, conteudo_bytes)
                peer.add_file(nome)
            else:
                print("Erro ao baixar o arquivo.")
        elif opcao == "6":
            break
        else:
            print("Opção inválida.")
