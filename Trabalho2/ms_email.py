import pika

class ms_email:
    def __init__(self):
        self.assinantes = {
            "Santos": ["Assinante_A", "Assinante_B"],
            "Rio de Janeiro" : ["Assinante_A"]
        }

    def execute(self):
        print("dale")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Declare 'viagem-santos'
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name_santos = result.method.queue
        channel.queue_bind(exchange='viagem-santos', queue=queue_name_santos)

        # Declare 'viagem-rio-janeiro'
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name_rj = result.method.queue
        channel.queue_bind(exchange='viagem-rio-janeiro', queue=queue_name_rj)

        def callback_santos(ch, method, properties, body):
            print("here")
            for assinante in self.assinantes["Santos"]:
                with open(f'Santos_{assinante}.txt', 'a') as file:
                    file.write(body.decode('utf-8') + '\n')

        def callback_rj(ch, method, properties, body):
            print("here")
            for assinante in self.assinantes["Santos"]:
                with open(f'Santos_{assinante}.txt', 'a') as file:
                    file.write(body.decode('utf-8') + '\n')

        channel.basic_consume(queue=queue_name_santos, on_message_callback=callback_santos, auto_ack=True)
        channel.basic_consume(queue=queue_name_rj, on_message_callback=callback_rj, auto_ack=True)
        channel.start_consuming()
