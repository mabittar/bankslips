import asyncio
import signal

from aiokafka import AIOKafkaConsumer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    sessionmaker,
)


from models.models import BankslipModel
from src.settings import settings
from routes.schema import BankslipDTO, BankslipRequest


engine = create_engine(
    settings.DATABASE_URI,
    echo=settings.ECHO_SQL,
)
Session = sessionmaker(
    bind=engine,
)


class Propagator:
    async def send_email(self, bs: BankslipDTO) -> BankslipDTO:
        if hasattr(bs, "propagated") and bs.propagated:
            return bs
        print(f"aqui envia arquivo: {bs.debt_id} para {bs.email}")
        bs.propagated = True
        return bs


class FileGenerator:
    async def generate_file(self, bs: BankslipRequest) -> BankslipDTO:
        if hasattr(bs, "bankslip_file"):
            return bs
        print(f"aqui gera arquivo: {bs.debt_id}")
        file = ""
        fetched_bankslip = BankslipDTO(
            **bs.model_dump(), bankslip_file=file, propagated=False
        )
        return fetched_bankslip


class MessageHandler:
    def __init__(self):
        self.session = Session

    async def get_bankslip(self, bankslip: BankslipRequest) -> BankslipDTO | None:
        print(f"check if {bankslip.debt_id} exists")
        existing = None
        with self.session() as conn:
            result = conn.scalars(
                select(BankslipModel).where(BankslipModel.debt_id == bankslip.debt_id)
            )
            existing = result.one_or_none()
        if existing:
            bs = BankslipDTO.model_validate(existing)
            bs.existing = True
            return bs
        else:
            None

    async def create_or_update_bankslip(self, bs: BankslipDTO):
        print(f"bankslip {bs.debt_id} finished, persisting")
        with self.session() as conn:
            if bs.existing:
                result = conn.scalars(
                    select(BankslipModel).where(BankslipModel.debt_id == bs.debt_id)
                )
                model = result.one()
                model.bankslip_file = bs.bankslip_file
                model.propagated = bs.propagated
            else:
                model = BankslipModel(**bs.model_dump(exclude="existing"))
                conn.add(model)
            conn.commit()

    async def handle_message(self, msg: BankslipRequest):
        """Kick off tasks for a given message.
        Args:
            msg (BankslipRequest): consumed message to process.
        """
        print("Got new message and start handling message.")
        fetcher = FileGenerator()
        propagator = Propagator()
        existing = await self.get_bankslip(msg)
        if existing and hasattr(existing, "propagated"):
            if existing.propagated:
                return
        bs = existing if existing is not None else msg
        bs = await fetcher.generate_file(bs)
        bs = await propagator.send_email(bs)
        await self.create_or_update_bankslip(bs)

    async def shutdown(self, loop, signal=None):
        if signal:
            print(f"Received exit signal {signal.name}...")
        tasks = [
            task
            for task in asyncio.all_tasks(loop)
            if task is not asyncio.current_task(loop)
        ]
        for task in tasks:
            task.cancel()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Finished awaiting cancelled tasks, results: {results}")
        loop.stop()

    def handle_exception(self, loop, context):
        msg = context.get("exception", context["message"])
        print(f"Caught exception: {msg}")
        print("Shutting down...")
        asyncio.create_task(self.shutdown(loop))


async def consume():
    loop = asyncio.get_event_loop()
    message_handler = MessageHandler()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(message_handler.shutdown(loop, signal=s))
        )
    loop.set_exception_handler(message_handler.handle_exception)
    consumer = AIOKafkaConsumer(
        settings.BANKSLIP_TOPIC,
        bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        group_id="newGroup",
    )
    await consumer.start()
    while True:
        try:
            async for msg in consumer:
                data = msg.value.decode("utf-8")
                bankslip = BankslipRequest.model_validate_json(data)
                await asyncio.create_task(
                    message_handler.handle_message(bankslip), name=bankslip.debt_id
                )
                print(f"Acked {bankslip.debt_id}")
        except Exception as e:
            print(e)
            continue
        # finally:
        #     await consumer.stop()


if __name__ == "__main__":
    print("Script running")
    asyncio.run(consume())
