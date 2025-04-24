import pika

class ms_marketing:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='viagem-santos', exchange_type='fanout')
        self.channel.exchange_declare(exchange='viagem-rio-janeiro', exchange_type='fanout')

    def execute(self, offers):
        print("oap")
        """Receive the new offers and send to clients"""

        for offer in offers:
            body = f"""Não perca essa oportunidade de ir para {offer["porto_desembarque"]}!
            Saindo de {offer["porto_embarque"]} no dia {offer["data"]}."""

            if offer["porto_desembarque"] == "Santos":
                # Publica na fila de santos
                print(body)
                self.channel.basic_publish(exchange='viagem-santos', routing_key='', body=body)
            elif offer["porto_desembarque"] == "Rio de Janeiro":
                # Publica na fila do rio
                print(body)
                self.channel.basic_publish(exchange='viagem-rio-janeiro', routing_key='', body=body)
            else:
                print("Sem fila configurada para essa promoção")

