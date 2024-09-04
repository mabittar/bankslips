from json import dumps
from typing import List
from aiokafka import AIOKafkaProducer
from ..settings import settings


class Kafka:
    def __init__(self):
        self.topic = (settings.BANKSLIP_TOPIC,)
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )

    @staticmethod
    def kafka_serializer(value) -> bytes:
        return dumps(value).encode()

    async def send_many(self, messages: List):
        try:
            await self.producer.start()

            try:
                for msg in messages:
                    await self.producer.send_and_wait(
                        self.topic, self.kafka_serializer(msg)
                    )
            finally:
                await self.producer.stop()

        except Exception as err:
            print(f"Some Kafka error: {err}")
