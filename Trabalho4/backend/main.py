import threading
import multiprocessing

from pagamento import pagamento
from ms_bilhete import ms_bilhete
from ms_reserva import ms_reserva
from ms_pagamento import ms_pagamento
from ms_marketing import ms_marketing
from ms_itinerarios import ms_itinerarios

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Gerar par de chaves
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # ou .PKCS8
    encryption_algorithm=serialization.NoEncryption()  # ou use senha se quiser
)

sistema_reserva = None

# Worker functions criam as instâncias dentro dos subprocessos
def run_bilhete(public_key_pem):
    sistema = ms_bilhete(public_key_pem)
    sistema.execute()

def run_pagamento(public_key_pem, private_key_pem):
    sistema = ms_pagamento(public_key_pem, private_key_pem)
    sistema.execute()

def run_itinerarios():
    sistema = ms_itinerarios()
    sistema.execute()

def run_reserva():
    sistema_reserva = ms_reserva(public_key_pem)
    sistema_reserva.execute()

def run_pagamento_out():
    sistema_pagamento = pagamento()
    sistema_pagamento.execute()

def run_marketing():
    sistema_marketing = ms_marketing()
    sistema_marketing.execute()

if __name__ == "__main__":
    # Criar e iniciar o processo para o sistema de pagamento
    processo_pagamento = multiprocessing.Process(target=run_pagamento, args=(public_key_pem,private_key_pem,))
    processo_pagamento.start()

    # Criar e iniciar o processo para o sistema de bilhete
    processo_bilhete = multiprocessing.Process(target=run_bilhete, args=(public_key_pem,))
    processo_bilhete.start()
    
    # Criar e iniciar o processo para o sistema de itinerarios
    processo_itinerarios = multiprocessing.Process(target=run_itinerarios, args=())
    processo_itinerarios.start()

    processo_pagamento2 = multiprocessing.Process(target=run_pagamento_out, args=())
    processo_pagamento2.start()

    # Criar e iniciar o processo para o sistema de reserva
    processo_reserva = threading.Thread(target=run_reserva, args=())
    processo_reserva.start()

    processo_marketing = threading.Thread(target=run_marketing, args=())
    processo_marketing.start()

    print("Sistemas iniciados com sucesso!")

    # Aguardar a conclusão do processo de pagamento
    processo_reserva.join()
    processo_bilhete.join()
    processo_pagamento.join()
    processo_pagamento2.join()
    processo_itinerarios.join()

    print("Execução concluída!")
