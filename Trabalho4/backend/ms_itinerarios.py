import uvicorn
import threading

from fastapi import FastAPI

class ms_itinerarios:
    def __init__(self):
        self._start_api()

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
        self.thread.join()

    def get_itinerarios(self):
        """Função para simular uma chamada no banco de dados"""
        
        # Datas disponíveis de partida, 
        # nome do navio, porto de embarque, 
        # porto de desembarque no retorno, 
        # lugares visitados, número de noites, 
        # valor por pessoa;

        return [
            {   
                "data": "01-01-2026",
                "nome_navio":"Benjamin", 
                "porto_embarque":"Santos",
                "porto_desembarque":"Santos",
                "lugares_visitados":"Fortaleza, Rio de Janeiro",
                "numero_noites": 3,
                "valor_por_pessoa": 500,
                "codigo":"DPII-00"
            },
            {   
                "data": "02-01-2026",
                "nome_navio":"Dom Pedro II", 
                "porto_embarque":"Santos",
                "porto_desembarque":"Santos",
                "lugares_visitados":"Fortaleza, Rio de Janeiro",
                "numero_noites": 3,
                "valor_por_pessoa": 500,
                "codigo":"DPII-01"
            },
        ]