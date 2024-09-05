from aiokafka import AIOKafkaProducer

from ..settings import settings


async def kafka_producer(messages):
    producer = AIOKafkaProducer(**settings.set_kafka_args)
    await producer.start()
    for message in messages:
        await producer.send(settings.BANKSLIP_TOPIC, message, partition=0)
    await producer.stop()
