import asyncio
import signal
import async_timeout

from aiokafka import AIOKafkaConsumer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    sessionmaker,
)


from .models import BankslipModel
from .settings import settings
from .schema import BankslipDTO, BankslipRequest

KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
BANKSLIP_TOPIC = "bankslip_process"

engine = create_engine(
    settings.DATABASE_URI,
    echo=settings.ECHO_SQL,
)
Session = sessionmaker(
    bind=engine,
)


class Propagator:
    async def send_email(self, msg: BankslipDTO) -> BankslipDTO:
        print(f"aqui envia arquivo: {msg.debt_id} para {msg.email}")
        sent_bankslip = BankslipDTO(**msg.model_dump(), propagated=True)
        return sent_bankslip


class FileGenerator:
    async def generate_file(self, msg: BankslipRequest) -> BankslipDTO:
        print(f"aqui gera arquivo: {msg.debt_id}")
        file = ""
        fetched_bankslip = BankslipDTO(**msg.model_dump(), bankslip_file=file)
        return fetched_bankslip


class KafkaConsumer:
    def __init__(self, loop):
        self.session = Session
        self.loop = loop
        self.consumer = AIOKafkaConsumer(
            BANKSLIP_TOPIC,
            loop=loop,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        )

    async def get_bankslip(self, bankslip: BankslipDTO) -> BankslipDTO | None:
        print(f"check if {bankslip.debt_id} exists")
        with self.session() as conn:
            result = await conn.scalars(
                select(BankslipModel).where(BankslipModel.debt_id == bankslip.debt_id)
            )
            existing = result.one_or_none()
        if existing:
            return BankslipDTO.model_validate(existing)
        else:
            None

    async def update_bankslip(self, bankslip: BankslipDTO):
        print(f"bankslip {bankslip.debt_id} finished, persisting")
        with self.session() as conn:
            conn.add(bankslip)
            conn.commit()

    async def handle_message(self, msg: BankslipRequest):
        """Kick off tasks for a given message.
        Args:
            msg (BankslipRequest): consumed message to process.
        """
        print("Creating event and start event handler.")
        existing = await self.get_bankslip(msg)
        if existing and existing.propagated:
            return
        fetcher = FileGenerator()
        propagator = Propagator()
        bs = await fetcher.generate_file(msg)
        if bs:
            propagator.send_email(bs)
            await self.update_bankslip(bs)
        print(f"Acked {msg.debt_id}")

    async def consume(self):
        seconds = 1
        while True:
            try:
                await self.consumer.start()
                async with async_timeout.timeout(seconds):
                    async for msg in self.consumer:
                        data = msg.value.decode("utf-8")
                        bankslip = BankslipRequest.model_validate_json(data)
                        await asyncio.create_task(
                            self.handle_message(bankslip), name=bankslip.debt_id
                        )
                    await asyncio.sleep(seconds)
            except asyncio.TimeoutError:
                print(f"No message on topic waiting for {seconds} seconds.")
                pass
            except Exception as ex:
                print(ex)
                continue

    async def shutdown(self, loop, signal=None):
        await self.consumer.stop()
        """Cleanup tasks tied to the service's shutdown."""
        if signal:
            print(f"Received exit signal {signal.name}...")
        tasks = []
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task(loop):
                task.cancel()
                tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Finished awaiting cancelled tasks, results: {results}")
        loop.stop()

    def handle_exception(self, loop, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        print(f"Caught exception: {msg}")
        print("Shutting down...")
        asyncio.create_task(self.shutdown(loop))


def main():
    loop = asyncio.get_event_loop()
    consumer = KafkaConsumer(loop)
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda: asyncio.create_task(consumer.shutdown(loop, signal=s))
        )
    loop.set_exception_handler(consumer.handle_exception)

    try:
        loop.create_task(consumer.consume())
        loop.run_forever()
    except KeyboardInterrupt:
        print("Process interrupted")
    finally:
        loop.close()
        print("Successfully shutdown the queue service.")


if __name__ == "__main__":
    main()
