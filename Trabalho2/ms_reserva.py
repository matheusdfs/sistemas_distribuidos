import pika
import time

class ms_reserva:
    def __init__(self):
        self.reservas = []

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='reserva-criada')
        self.channel.queue_declare(queue='pagamento-aprovado')
        self.channel.queue_declare(queue='pagamento-recusado')
        self.channel.queue_declare(queue='bilhete-gerado')

    def execute(self):
        while True:
            self.menu()

    def menu(self):
        print("Bem-vindo ao sistema de reservas de passagens!")
        print("Escolha uma das opções abaixo:")
        print("1. Consultar itinerários disponíveis")
        print("2. Reservar passagem")
        print("3. Sair")

        opcao = input()

        print("\n\n")
        
        if opcao == "1":
            self.consultar_itinerarios()
        elif opcao == "2":
            self.reservar_passagem()
        elif opcao == "3":
            exit()
        else:
            print("Opção inválida. Tente novamente.")

    def consultar_itinerarios(self):
        itinerarios = self.get_itinerarios()

        for itinerario in itinerarios:
            print(f"{itinerario['codigo']}: {itinerario['porto_embarque']} - {itinerario['lugares_visitados']} - {itinerario['porto_desembarque']} em {itinerario['data']}")

        print("\n\n")

    def reservar_passagem(self):
        print("Insira o código do itinerário desejado:")
        codigo = input()

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
                "itinerario": itinerario_selecionado,
                "user": "Diniz",
            }

            # Adiciona a reserva à lista de reservas
            self.channel.basic_publish(exchange='', routing_key='reserva-criada', body=str(body))

            # TODO: Mostrar progresso
            self.show_progress(itinerario_selecionado)
        else:
            print("Código de itinerário inválido. Tente novamente.")

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
     
    