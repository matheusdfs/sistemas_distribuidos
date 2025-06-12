import ast
import pika
import uvicorn
import threading

from fastapi import FastAPI

class ms_itinerarios:
    def __init__(self):
        # TODO : Mostrar e atualizar disponibilidades de cabines
        self._start_api()
        self.itinerarios = [
            {   
                "data": "01-01-2026",
                "nome_navio":"Benjamin", 
                "porto_embarque":"Santos",
                "porto_desembarque":"Santos",
                "lugares_visitados":"Fortaleza, Rio de Janeiro",
                "cabines_disponíveis": 10,
                "valor_por_pessoa": 500,
                "codigo":"DPII-00"
            },
            {   
                "data": "02-01-2026",
                "nome_navio":"Dom Pedro II", 
                "porto_embarque":"Santos",
                "porto_desembarque":"Santos",
                "lugares_visitados":"Fortaleza, Rio de Janeiro",
                "cabines_disponíveis": 10,
                "valor_por_pessoa": 500,
                "codigo":"DPII-01"
            },
        ]

    def _start_api(self):
        app = FastAPI()

        # Declaration of the endpoints
        @app.get("/get_itinerarios")
        def get_itinerarios():
            return self.get_itinerarios()

        # Run in thread so the code is not blocked
        self.thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={
            "host": "127.0.0.1",
            "port": 8001,
            "log_level": "info"
        }, daemon=True)
        self.thread.start()

    def execute(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='reserva-criada')
        channel.queue_declare(queue='reserva-cancelada')

        def callback_criada(ch, method, properties, body):
            data = ast.literal_eval(body.decode())
            codigo = data["codigo"]
            for itinerario in self.itinerarios:
                if itinerario["codigo"] == codigo and itinerario["cabines_disponíveis"] > 0:
                    itinerario["cabines_disponíveis"] -= 1
                    break

        def callback_cancelada(ch, method, properties, body):
            print("Reserva cancelada")
            data = ast.literal_eval(body.decode())
            codigo = data["codigo"]

            # Remove the user prefix
            codigo = codigo.replace("diniz_", "")
            for itinerario in self.itinerarios:
                if itinerario["codigo"] == codigo and itinerario["cabines_disponíveis"] > 0:
                    itinerario["cabines_disponíveis"] += 1
                    break

        channel.basic_consume(queue='reserva-criada', on_message_callback=callback_criada, auto_ack=True)
        channel.basic_consume(queue='reserva-cancelada', on_message_callback=callback_cancelada, auto_ack=True)
        channel.start_consuming()
        # self.thread.join()

    def get_itinerarios(self):
        """Função para simular uma chamada no banco de dados"""
        return self.itinerarios