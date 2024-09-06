from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.database import Postgresql
from diagrams.onprem.queue import Kafka
from diagrams.programming.framework import FastAPI
from diagrams.aws.engagement import SES 
from diagrams.generic.database import SQL

with Diagram("Arquitetura de Boletos", filename="solucao", show=False, outformat="jpg"):
    user = User("Usuário")
    
    with Cluster("API de Boletos"):
        api = FastAPI("API Rest")
        csv_validation = Server("Validação CSV")
        api >> csv_validation
    
    with Cluster("Kafka Pub/Sub"):
        kafka_producer = Kafka("Kafka Producer")
        kafka_consumer = Kafka("Kafka Consumer")
        api >> Edge(label="Envia mensagens") >> kafka_producer
        kafka_producer >> Edge(label="Distribui mensagens") >> kafka_consumer
    
    with Cluster("Serviços de Processamento"):
        with Cluster("Consumidores Replicáveis"):
            consumer = Server("Consumidor Python")
        
        with Cluster("Banco de Dados"):
            db = Postgresql("Postgres DB")
            adminer = SQL("Adminer")

        external_service = Server("Serviço Externo de Boletos")
        email_service = SES("Serviço de E-mail")

        kafka_consumer >> Edge(label="Verifica e Processa") >> consumer
        consumer >> Edge(label="Busca ou Atualiza") >> db
        consumer >> Edge(label="Gera Boletos") >> external_service
        external_service >> Edge(label="Retorno") >> consumer
        consumer >> Edge(label="Envia Email") >> email_service
        consumer >> Edge(label="Atualiza Status") >> db
    
    user >> Edge(label="CSV Upload") >> api
    db >> adminer
