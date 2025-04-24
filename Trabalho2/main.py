import pika
import multiprocessing

multiprocessing.set_start_method('fork')

from ms_bilhete import ms_bilhete
from ms_reserva import ms_reserva
from ms_pagamento import ms_pagamento

# Função para rodar os workers
def run_worker(worker_instance):
    worker_instance.execute()

if __name__ == "__main__":
    # Criar instâncias dos sistemas
    sistema_reserva = ms_reserva()
    sistema_bilhete = ms_bilhete()
    sistema_pagamento = ms_pagamento()

    # Criar e iniciar o processo para o sistema de pagamento
    processo_pagamento = multiprocessing.Process(target=run_worker, args=(sistema_pagamento,))
    processo_pagamento.start()

    # Criar e iniciar o processo para o sistema de bilhete
    processo_bilhete = multiprocessing.Process(target=run_worker, args=(sistema_bilhete,))
    processo_bilhete.start()

    # Executar a reserva no processo principal
    sistema_reserva.execute()

    # Aguardar a conclusão do processo de pagamento
    processo_pagamento.join()

    print("Execução concluída!")
