import multiprocessing

multiprocessing.set_start_method('fork')

from ms_email import ms_email
from ms_marketing import ms_marketing

# Função para rodar os workers
def run_worker(worker_instance):
    worker_instance.execute()

if __name__ == "__main__":
    # Criar instâncias dos sistemas
    sistema_marketing = ms_marketing()
    sistema_email = ms_email()

    # Criar e iniciar o processo para o sistema de pagamento
    processo_marketing = multiprocessing.Process(target=run_worker, args=(sistema_marketing,))
    processo_marketing.start()

    processo_email = multiprocessing.Process(target=run_worker, args=(sistema_email,))
    processo_email.start()

    processo_email.join()
    processo_marketing.join()


