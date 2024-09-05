from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class BankslipRequest(BaseModel):
    name: str = Field(description="nome")
    government_id: str = Field(description="numero do documento")
    email: EmailStr = Field(description="e-mail do sacado")
    debt_amount: int = Field(description="valor da cobrança")
    debt_due_date: date = Field(description="Data para ser paga")
    debt_id: str = Field(description=" uuid para o débito")


class BankslipDTO(BankslipRequest):
    bankslip_file: Optional[str] = Field(description="repesentacao do documento")
    propagated: Optional[bool] = Field(description="cobrança enviada")
    existing: Optional[bool] = Field(description="cobrança já existe na base", default=False, exclude=True)

    class Config:
        from_attributes = True
