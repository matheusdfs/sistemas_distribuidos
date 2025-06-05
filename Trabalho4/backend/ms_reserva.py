import ast
import pika
import json
import uvicorn
import requests
import threading

from fastapi import FastAPI
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

reservas = []

class ms_reserva:
    def __init__(self, public_key_pem):
        # Initialize variables
        self.public_key = serialization.load_pem_public_key(public_key_pem)

        # Set connection with rabbitmq server
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='reserva-criada')

        # Start API of the service
        self._start_api()

    def _start_api(self):
        app = FastAPI()

        # Declaration of the endpoints
        @app.get("/get_itinerarios")
        def get_itinerarios():
            return self.get_itinerarios()
        
        @app.get("/reservar_passagem")
        def reservar_passagem(codigo_itinerario : str):
            return self.reservar_passagem(codigo_itinerario)
        
        @app.get("/cancelar_reserva")
        def cancelar_reserva(codigo_reserva : str):
            return self.cancelar_reserva(codigo_reserva)

        # Run in thread so the code is not blocked
        threading.Thread(target=uvicorn.run, args=(app,), kwargs={
            "host": "127.0.0.1",
            "port": 8000,
            "log_level": "info"
        }, daemon=True).start()

    def get_itinerarios(self):
        # Request to the ms_itinerarios endpoint
        response = requests.get("http://localhost:8001/get_itinerarios")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "FAIL_GET_ITINERARIOS"}

    def reservar_passagem(self, codigo_itinerario):
        itinerarios = self.get_itinerarios()
        itinerario_selecionado = next((itinerario for itinerario in itinerarios if itinerario["codigo"] == codigo_itinerario), None)

        if itinerario_selecionado:
            body = {
                "user": "diniz",
                "codigo": codigo_itinerario,
            }

            # Adiciona a reserva à lista de reservas
            self.channel.basic_publish(exchange='', routing_key='reserva-criada', body=str(body))

            reservas.append({"codigo":f"diniz_{codigo_itinerario}", "status": "reservado"})
        else:
            return {"error" : "CODE_NOT_FOUND"}
        
        return {
            "link_pagamento": self.criar_pagamento()["link_pagamento"],
            "codigo_reserva": f"diniz_{codigo_itinerario}"
        }
    
    def cancelar_reserva(self, codigo_reserva):
        resultado = [item for item in reservas if item["codigo"] == codigo_reserva]
        
        if not resultado:
            return {"error": "RESERVA_NOT_FOUND"}

        reservas.remove(resultado[0])
        return {"message": "RESERVA_CANCELADA"}

    def criar_pagamento(self):
        response = requests.get("http://localhost:8002/criar_pagamento")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "FAIL_CREATE_PAYMENT"}

    def execute(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
    
        channel.queue_declare(queue='pagamento-recusado')
        channel.queue_declare(queue='bilhete-gerado')

        result = channel.queue_declare(queue='', exclusive=True)
        queue_pagamento_aprovado = result.method.queue

        # self.channel.queue_declare(queue='pagamento-aprovado')
        channel.queue_bind(exchange='pagamento-aprovado', queue=queue_pagamento_aprovado)

        def callback_aprovado(ch, method, properties, body):
            data = ast.literal_eval(body.decode('utf-8'))

            #self.public_key.verify(
            #    data["assinatura"],
            #    data["body"],
            #   padding.PSS(
            #        mgf=padding.MGF1(hashes.SHA256()),
            #        salt_length=padding.PSS.MAX_LENGTH
            #    ),
            #    hashes.SHA256()
            #)

            data = ast.literal_eval(data["body"].decode('utf-8'))

            resultado = [item for item in reservas if item["codigo"] == f"{data['user']}_{data['codigo']}"]
            
            reservas.remove(resultado[0])

            temp = data["user"]
            temp_2 = data["codigo"]

            reservas.append({"codigo":f"{temp}_{temp_2}", "status": "aprovado"})


        def callback_gerado(ch, method, properties, body):
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

            data = ast.literal_eval(data["body"].decode('utf-8'))

            resultado = [item for item in reservas if item["codigo"] == f"{data['user']}_{data['codigo']}"]
            
            reservas.remove(resultado[0])

            temp = data["user"]
            temp_2 = data["codigo"]

            reservas.append({"codigo":f"{temp}_{temp_2}", "status": "bilhete_gerado"})
            # reservas.append({"codigo":f"{data["user"]}_{data["codigo"]}", "status": "bilhete_gerado"})

        def callback_recusado(ch, method, properties, body):
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

            data = ast.literal_eval(data["body"].decode('utf-8'))

            resultado = [item for item in reservas if item["codigo"] == f"{data['user']}_{data['codigo']}"]
            
            reservas.remove(resultado[0])

        channel.basic_consume(queue='bilhete-gerado', on_message_callback=callback_gerado, auto_ack=True)
        channel.basic_consume(queue='pagamento-recusado', on_message_callback=callback_recusado, auto_ack=True)
        channel.basic_consume(queue=queue_pagamento_aprovado, on_message_callback=callback_aprovado, auto_ack=True)
        channel.start_consuming()
     
    