import pika
import time
import uvicorn
import requests
import threading

from fastapi import FastAPI, Request
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

class ms_pagamento():
    def __init__(self, public_key_pem, private_key_pem):
        self.public_key = serialization.load_pem_public_key(public_key_pem)
        self.private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None  # ou passe a senha se estiver criptografada
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='pagamento-recusado')
        self.channel.exchange_declare(exchange='pagamento-aprovado', exchange_type='fanout')

        self._start_api()
    
    def _start_api(self):
        app = FastAPI()

        # Declaration of the endpoints
        @app.get("/criar_pagamento")
        def criar_pagamento(codigo_reserva: str):
            return self.criar_pagamento(codigo_reserva)["link_pagamento"]
        
        @app.post("/resultado_pagamento")
        async def resultado_pagamento(request: Request):
            req = await request.json()

            body = {
                "user": "diniz",
                "codigo": req["codigo_reserva"],
            }

            #assinatura = self.private_key.sign(
            #    body,
            #    padding.PSS(
            #        mgf=padding.MGF1(hashes.SHA256()),
            #        salt_length=padding.PSS.MAX_LENGTH
            #    ),
            #    hashes.SHA256()
            #)
            data = dict()
            data["body"] = body
            data["assinatura"] = None

            time.sleep(3)
            
            if req["status"] == "aprovado":
                print(f"[DEBUG] Pagamento aprovado para compra")
                self.channel.basic_publish(exchange='pagamento-aprovado', routing_key='', body=str(data))
            else:
                print(f"[DEBUG] Pagamento recusado para compra")
                self.channel.basic_publish(exchange='', routing_key='pagamento-recusado', body=str(data))

        # Run in thread so the code is not blocked
        self.thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={
            "host": "127.0.0.1",
            "port": 8002,
            "log_level": "info"
        }, daemon=True)
        self.thread.start()

    def criar_pagamento(self, codigo_reserva):
        response = requests.get(f"http://localhost:8003/criar_pagamento/", params={"codigo_reserva": codigo_reserva})
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "FAIL_CREATE_PAYMENT"}

    def execute(self):
        self.thread.join()
