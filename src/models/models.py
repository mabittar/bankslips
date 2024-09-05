from datetime import datetime
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import TIMESTAMP, func


class Base(DeclarativeBase):

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda x: datetime.now(),
        server_default=func.now(),
    )
    updated_on: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda x: datetime.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )


class BankslipModel(Base):
    __tablename__ = "bankslips"
    name: Mapped[str] = mapped_column(nullable=False)
    government_id: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    debt_amount: Mapped[float] = mapped_column(nullable=False)
    debt_due_date: Mapped[datetime] = mapped_column(nullable=False)
    debt_id: Mapped[str] = mapped_column(nullable=False, primary_key=True, unique=True)
    bankslip_file: Mapped[str] = mapped_column(nullable=True)
    propagated: Mapped[bool] = mapped_column(nullable=False, default=False)
