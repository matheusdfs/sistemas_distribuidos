import pika
import time
import random

class ms_pagamento():
    def __init__(self):
        pass

    def execute(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='reserva-criada')
        self.channel.queue_declare(queue='pagamento-aprovado')
        self.channel.queue_declare(queue='pagamento-recusado')

        def callback(ch, method, properties, body):
            """Função para validar pagamentos, 70% de chance de sucesso e 30% de falha"""
            time.sleep(2)
            if random.random() > 0.3:
                print(f"Pagamento aprovado para compra: {body}")
                self.channel.basic_publish(exchange='', routing_key='pagamento-aprovado', body=body)
            else:
                print(f"Pagamento recusado para compra: {body}")
                self.channel.basic_publish(exchange='', routing_key='pagamento-recusado', body=body)

        self.channel.basic_consume(queue='reserva-criada', on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
