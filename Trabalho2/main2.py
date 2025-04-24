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
    processo_pagamento = multiprocessing.Process(target=run_worker, args=(sistema_email,))
    processo_pagamento.start()

    sistema_marketing.execute(
        offers=[{   
            "data": "01-01-2026",
            "nome_navio":"Benjamin", 
            "porto_embarque":"Santos",
            "porto_desembarque":"Santos",
            "lugares_visitados":"Fortaleza, Rio de Janeiro",
            "numero_noites": 3,
            "valor_por_pessoa": 300,
            "codigo":"DPII-00"
        },
        {   
            "data": "01-01-2026",
            "nome_navio":"Benjamin", 
            "porto_embarque":"Santos",
            "porto_desembarque":"Rio de Janeiro",
            "lugares_visitados":"Fortaleza, Rio de Janeiro",
            "numero_noites": 3,
            "valor_por_pessoa": 300,
            "codigo":"DPII-00"
        }]
    )
