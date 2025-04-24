import time
import pika

class ms_bilhete:
    def __init__(self):
        pass

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
            time.sleep(3)
            print(f"Bilhete gerado para compra: {body}")
            self.channel.basic_publish(exchange='', routing_key='bilhete-gerado', body=body)

        self.channel.basic_consume(queue=self.queue_pagamento_aprovado, on_message_callback=callback, auto_ack=True)
        # self.channel.basic_consume(queue='pagamento-aprovado', on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()