import ast
import pika
import uvicorn
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

        # Run in thread so the code is not blocked
        threading.Thread(target=uvicorn.run, args=(app,), kwargs={
            "host": "127.0.0.1",
            "port": 8000,
            "log_level": "info"
        }, daemon=True).start()

    def reservar_passagem(self, codigo=None):
        itinerarios = self.get_itinerarios()
        itinerario_selecionado = next((itinerario for itinerario in itinerarios if itinerario["codigo"] == codigo), None)

        if itinerario_selecionado:
            # O MS Reserva retorna um link de pagamento para o cliente, 
            # cria a reserva e publica uma mensagem na fila reserva- criada, 
            # notificando o MS Pagamento de que uma nova reserva foi realizada;

            print("Itinerário selecionado:")
            print(f"{itinerario_selecionado['codigo']}: {itinerario_selecionado['porto_embarque']} - {itinerario_selecionado['lugares_visitados']} - {itinerario_selecionado['porto_desembarque']} em {itinerario_selecionado['data']}")
            print(f"Valor por pessoa: R${itinerario_selecionado['valor_por_pessoa']}")
            print("Reserva realizada com sucesso!")

            print("\n\n")

            print("Para realizar o pagamento, por favor utilizar o link: htpps://diniz_pagamento.com.br")

            body = {
                "user": "diniz",
                "codigo": codigo,
            }

            # Adiciona a reserva à lista de reservas
            self.channel.basic_publish(exchange='', routing_key='reserva-criada', body=str(body))

            reservas.append({"codigo":f"diniz_{codigo}", "status": "reservado"})

            print(f"Reserva criada com sucesso! Use o código diniz_{codigo} para verificar o status da reserva.")
        else:
            print("Código de itinerário inválido. Tente novamente.")

        print("\n\n")

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

            self.public_key.verify(
                data["assinatura"],
                data["body"],
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            data = ast.literal_eval(data["body"].decode('utf-8'))

            resultado = [item for item in reservas if item["codigo"] == f"{data['user']}_{data['codigo']}"]
            
            reservas.remove(resultado[0])

            temp = data["user"]
            temp_2 = data["codigo"]

            reservas.append({"codigo":f"{temp}_{temp_2}", "status": "aprovado"})


        def callback_gerado(ch, method, properties, body):
            data = ast.literal_eval(body.decode('utf-8'))

            self.public_key.verify(
                data["assinatura"],
                data["body"],
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            data = ast.literal_eval(data["body"].decode('utf-8'))

            resultado = [item for item in reservas if item["codigo"] == f"{data['user']}_{data['codigo']}"]
            
            reservas.remove(resultado[0])

            temp = data["user"]
            temp_2 = data["codigo"]

            reservas.append({"codigo":f"{temp}_{temp_2}", "status": "bilhete_gerado"})
            # reservas.append({"codigo":f"{data["user"]}_{data["codigo"]}", "status": "bilhete_gerado"})

        def callback_recusado(ch, method, properties, body):
            data = ast.literal_eval(body.decode('utf-8'))

            self.public_key.verify(
                data["assinatura"],
                data["body"],
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            data = ast.literal_eval(data["body"].decode('utf-8'))

            resultado = [item for item in reservas if item["codigo"] == f"{data['user']}_{data['codigo']}"]
            
            reservas.remove(resultado[0])

        channel.basic_consume(queue='bilhete-gerado', on_message_callback=callback_gerado, auto_ack=True)
        channel.basic_consume(queue='pagamento-recusado', on_message_callback=callback_recusado, auto_ack=True)
        channel.basic_consume(queue=queue_pagamento_aprovado, on_message_callback=callback_aprovado, auto_ack=True)
        channel.start_consuming()

    def show_progress(self):
        print("Insira o código da reserva:")
        codigo = input()

        print("\n\n")
        
        resultado = next((item for item in reservas if item["codigo"] == codigo), None)
        print(resultado)

        print("\n\n")

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

if __name__ == "__main__":
    sistema_reserva = ms_reserva()
    sistema_reserva.menu()
     
    