import pika
import time

class ms_marketing:
    def __init__(self):
        self.offers = [{
            "data": "01-01-2026",
            "nome_navio":"Benjamin", 
            "porto_embarque":"Santos",
            "porto_desembarque":"Rio de Janeiro",
            "lugares_visitados":"Fortaleza, Rio de Janeiro",
            "numero_noites": 3,
            "valor_por_pessoa": 150,
            "codigo":"PROMO-RIO"
        }]

    def execute(self):
        """Receive the new offers and send to clients"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        
        self.channel.queue_declare(queue='promocoes')

        time.sleep(10)

        while True:

            self.channel.basic_publish(
                exchange='',
                routing_key='promocoes',
                body="Use o código de itinerário PROMO-RIO para conseguir 60% de desconto na viagem SP/RJ\n\n"
            )

            time.sleep(60)

