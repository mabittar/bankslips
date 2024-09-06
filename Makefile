# Nome do arquivo: Makefile

# Variáveis para facilitar a manutenção
DOCKER_COMPOSE = docker-compose
KAFKA_CONTAINER = kafka
TOPIC_NAME = bankslip_process
PARTITIONS = 6
REPLICATION_FACTOR = 1
KAFKA_PORT = 29092

# Passo 1: Parar e remover todos os containers ativos
.PHONY: clean
clean:
	@echo "Parando e removendo todos os containers ativos..."
	docker stop $$(docker ps -q) || true
	docker rm $$(docker ps -aq) || true

# Passo 2: Subir os containers sem o serviço de criação de tópicos
.PHONY: up
up:
	@echo "Subindo os serviços com Docker Compose..."
	$(DOCKER_COMPOSE) up -d --remove-orphans

# Passo 3: Construir a imagem do consumidor Kafka
.PHONY: build-consumer
build-consumer:
	@echo "Construindo a imagem do consumidor Kafka..."
	docker build -f Dockerfile-consumer -t kafka-consumer-app .

# Passo 4: Executar o container do consumidor Kafka com volume e rede configurados
.PHONY: run-consumer
run-consumer:
	@echo "Executando o container do consumidor Kafka..."
	docker run --name kafka-consumer \
	-e KAFKA_BOOTSTRAP_SERVERS="kafka:29092" \
	-e POSTGRES_SERVER="db" \
	-e POSTGRES_PASSWORD="changethis" \
	-e POSTGRES_USER="admin" \
	-e POSTGRES_DB="bankslip" \
	-e POSTGRES_PORT="5432" \
	-e POSTGRES_DRIVER="psycopg" \
	--network bankslip_bankslip-net \
	kafka-consumer-app

# Passo 5: Comando completo para rodar o processo
.PHONY: start
start: clean up
