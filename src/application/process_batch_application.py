from typing import List


from .base_application import BaseApplication
from ..schema import BankslipRequest
from ..infra.kakfa_connector import Kafka


class ProcessBatchApplication(BaseApplication):
    def __init__(self):
        self.kafka = Kafka()

    async def execute(self, input: List[BankslipRequest]):
        try:
            bankslips = [bs.model_dump() for bs in input]
            self.kafka.send_many(bankslips)
        except Exception as e:
            print(f"Some process batch application error: {e}")
            raise e
