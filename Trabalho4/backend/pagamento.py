import time
import random
import uvicorn
import requests
import threading

from fastapi import FastAPI

class pagamento():
    def __init__(self):
        self._start_api()
    
    def _start_api(self):
        app = FastAPI()

        # Declaration of the endpoints
        @app.get("/criar_pagamento")
        def criar_pagamento(codigo_reserva: str):
            random_id = random.randint(100000, 999999)
            link_pagamento = f"https://dinizpaymentplataform.com/pay/{random_id}"
            threading.Thread(target=self.process_payment, args=(codigo_reserva,), daemon=True).start()
            return {"link_pagamento": link_pagamento}

        # Run in thread so the code is not blocked
        self.thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={
            "host": "127.0.0.1",
            "port": 8003,
            "log_level": "info"
        }, daemon=True)
        self.thread.start()

    def execute(self):
        self.thread.join()

    def process_payment(self, codigo_reserva):
        time.sleep(3)
        data = None
        if random.random() > 0.3:
            data = {
                "status": "aprovado",
                "codigo_reserva": codigo_reserva,
            }
        else:
            data = {
                "status": "recusado",
                "codigo_reserva": codigo_reserva,
            }

        url = "http://localhost:8002/resultado_pagamento/"

        response = requests.post(url, json=data)
        if response.status_code != 200:
            print("ERROR PROCESSING PAYMENT")
        
