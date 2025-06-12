import ast
import time
import pika

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class ms_bilhete:
    def __init__(self, public_key_pem):
        self.public_key = serialization.load_pem_public_key(public_key_pem)

    def execute(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='bilhete-gerado')
        
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_pagamento_aprovado = result.method.queue

        # self.channel.queue_declare(queue='pagamento-aprovado')
        self.channel.queue_bind(exchange='pagamento-aprovado', queue=self.queue_pagamento_aprovado)

        def callback(ch, method, properties, body):
            data = ast.literal_eval(body.decode('utf-8'))

            #self.public_key.verify(
            #    data["assinatura"],
            #    data["body"],
            #    padding.PSS(
            #        mgf=padding.MGF1(hashes.SHA256()),
            #        salt_length=padding.PSS.MAX_LENGTH
            #    ),
            #    hashes.SHA256()
            #)

            time.sleep(3)
            
            self.channel.basic_publish(exchange='', routing_key='bilhete-gerado', body=body)

        self.channel.basic_consume(queue=self.queue_pagamento_aprovado, on_message_callback=callback, auto_ack=True)
        # self.channel.basic_consume(queue='pagamento-aprovado', on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()