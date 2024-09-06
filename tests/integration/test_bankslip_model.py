from datetime import datetime
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import BankslipModel

@pytest.mark.anyio(backend="asyncio")
async def test_create_bankslip(session: AsyncSession):
    # Criação de um registro no modelo Bankslip
    bankslip = BankslipModel(
        name="John Doe",
        government_id="123456789",
        email="john.doe@example.com",
        debt_amount=1000.0,
        debt_due_date=datetime(2024, 1, 19),
        debt_id="uuid-1234"
    )
    
    session.add(bankslip)
    await session.commit()

    # Buscar o registro criado
    result = await session.get(BankslipModel, "uuid-1234")
    assert result is not None
    assert result.name == "John Doe"