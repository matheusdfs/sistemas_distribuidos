import ast
import pika
import time
import random

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives import serialization


class ms_pagamento():
    def __init__(self, public_key_pem, private_key_pem):
        self.public_key = serialization.load_pem_public_key(public_key_pem)
        self.private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None  # ou passe a senha se estiver criptografada
        )

    def execute(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='reserva-criada')
        self.channel.queue_declare(queue='pagamento-recusado')
        # self.channel.queue_declare(queue='pagamento-aprovado')
        self.channel.exchange_declare(exchange='pagamento-aprovado', exchange_type='fanout')

        def callback(ch, method, properties, body):
            """Função para validar pagamentos, 70% de chance de sucesso e 30% de falha"""
            assinatura = self.private_key.sign(
                body,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            data = dict()
            data["body"] = body
            data["assinatura"] = assinatura

            time.sleep(3)
            
            if random.random() > 0.3:
                print(f"[DEBUG] Pagamento aprovado para compra")
                # self.channel.basic_publish(exchange='', routing_key='pagamento-aprovado', body=body)
                self.channel.basic_publish(exchange='pagamento-aprovado', routing_key='', body=str(data))
            else:
                print(f"[DEBUG] Pagamento recusado para compra")
                self.channel.basic_publish(exchange='', routing_key='pagamento-recusado', body=str(data))

        self.channel.basic_consume(queue='reserva-criada', on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
