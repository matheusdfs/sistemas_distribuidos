import pika

class ms_email:
    def __init__(self):
        self.assinantes = {
            "Santos": ["Assinante_A", "Assinante_B"],
            "Rio de Janeiro" : ["Assinante_A"]
        }

    def execute(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Declare 'viagem-santos'
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name_santos = result.method.queue
        channel.queue_bind(exchange='viagem-santos', queue=queue_name_santos)

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name_rio = result.method.queue
        channel.queue_bind(exchange='viagem-rio', queue=queue_name_rio)

        def callback_santos(ch, method, properties, body):
            for assinante in self.assinantes["Santos"]:
                with open(f'Santos_{assinante}.txt', 'a') as file:
                    file.write(body.decode('utf-8') + '\n')

        def callback_rio(ch, method, properties, body):
            for assinante in self.assinantes["Rio de Janeiro"]:
                with open(f'Rio_{assinante}.txt', 'a') as file:
                    file.write(body.decode('utf-8') + '\n')

        channel.basic_consume(queue=queue_name_santos, on_message_callback=callback_santos, auto_ack=True)
        channel.basic_consume(queue=queue_name_rio, on_message_callback=callback_rio, auto_ack=True)
        channel.start_consuming()
