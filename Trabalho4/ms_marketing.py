import pika
import time

class ms_marketing:
    def __init__(self):
        self.offers = offers=[{   
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

    def execute(self):
        """Receive the new offers and send to clients"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange='viagem-santos', exchange_type='fanout')
        self.channel.exchange_declare(exchange='viagem-rio', exchange_type='fanout')

        time.sleep(2)

        for offer in self.offers:
            body = f"""Não perca essa oportunidade de ir para {offer["porto_desembarque"]}!
            Saindo de {offer["porto_embarque"]} no dia {offer["data"]}."""

            if offer["porto_desembarque"] == "Santos":
                # Publica na fila de santos
                self.channel.basic_publish(exchange='viagem-santos', routing_key='', body=body)
            elif offer["porto_desembarque"] == "Rio de Janeiro":
                # Publica na fila do rio
                self.channel.basic_publish(exchange='viagem-rio', routing_key='', body=body)
            else:
                print("Sem fila configurada para essa promoção")

