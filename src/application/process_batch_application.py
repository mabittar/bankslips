from typing import List
from json import dumps


from .base_application import BaseApplication
from ..infra.kafka import kafka_producer
from ..routes.schema import BankslipRequest


class ProcessBatchApplication(BaseApplication):
    @staticmethod
    def kafka_serializer(value) -> bytes:
        return dumps(value).encode()

    async def execute(self, parsed_data: List[BankslipRequest]):
        try:
            bankslips = [bs.model_dump_json().encode() for bs in parsed_data]
            await kafka_producer(bankslips)
        except Exception as e:
            print(f"Some process batch application error: {e}")
            raise e
