import threading
import multiprocessing

multiprocessing.set_start_method('fork')

from ms_bilhete import ms_bilhete
from ms_reserva import ms_reserva
from ms_pagamento import ms_pagamento

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Gerar par de chaves
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

# Função para rodar os workers
def run_worker(worker_instance):
    worker_instance.execute()

if __name__ == "__main__":
    # Criar instâncias dos sistemas
    sistema_bilhete = ms_bilhete(public_key)
    sistema_pagamento = ms_pagamento(public_key, private_key)

    # Criar e iniciar o processo para o sistema de pagamento
    processo_pagamento = multiprocessing.Process(target=run_worker, args=(sistema_pagamento,))
    processo_pagamento.start()

    # Criar e iniciar o processo para o sistema de bilhete
    processo_bilhete = multiprocessing.Process(target=run_worker, args=(sistema_bilhete,))
    processo_bilhete.start()

    # Executar a reserva no processo principal
    sistema_reserva = ms_reserva(public_key)

    processo_reserva = threading.Thread(target=run_worker, args=(sistema_reserva,))
    processo_reserva.start()

    sistema_reserva.menu()

    # Aguardar a conclusão do processo de pagamento
    processo_pagamento.join()

    print("Execução concluída!")
