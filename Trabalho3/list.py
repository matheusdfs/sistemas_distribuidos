import Pyro5.api

# Localiza o Name Server
ns = Pyro5.api.locate_ns()

# Lista todos os objetos registrados
registrados = ns.list()

# Exibe os nomes e URIs dos objetos registrados
for nome, uri in registrados.items():
    print(f"{nome} -> {uri}")
