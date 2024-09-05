from http import HTTPStatus
from fastapi import APIRouter, UploadFile, HTTPException
import pandas as pd
from pydantic import ValidationError
from sqlalchemy import select


from ..application.process_batch_application import ProcessBatchApplication
from ..infra.db import SessionDep
from ..models.models import BankslipModel
from ..settings import settings
from .schema import BankslipDTO, BankslipRequest

router = APIRouter(tags=["bankslip"], prefix="/bankslip")


@router.get("/{debt_id}", status_code=HTTPStatus.OK)
async def get(session: SessionDep, debt_id: str) -> BankslipDTO:
    result = await session.scalars(
        select(BankslipModel).where(BankslipModel.debt_id == debt_id)
    )
    existing = result.one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Bankslip not found")
    return BankslipDTO.model_validate(existing)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create(session: SessionDep, body: BankslipRequest) -> BankslipDTO:
    result = await session.scalars(
        select(BankslipModel).where(BankslipModel.debt_id == body.debt_id)
    )
    existing = result.one_or_none()
    if existing:
        return BankslipDTO.model_validate(existing)
    bankslip = BankslipModel(**body.model_dump())
    session.add(bankslip)
    session.commit()
    session.refresh(bankslip)
    return BankslipDTO.model_validate(bankslip)


def process_row(row) -> tuple[BankslipRequest, None] | tuple[None, str]:
    try:
        data = BankslipRequest(
            name=row["name"],
            government_id=str(row["governmentId"]),
            email=row["email"],
            debt_amount=int(row["debtAmount"]),
            debt_due_date=row["debtDueDate"],
            debt_id=row["debtId"],
        )
        return data, None
    except ValidationError as e:
        return None, str(e)


@router.post("/batch", status_code=HTTPStatus.CREATED)
async def batch_process(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No upload file sent")
    process_batch = ProcessBatchApplication()
    failed_rows = []
    parsed_data = []
    try:
        for chunk in pd.read_csv(file.file, chunksize=settings.CHUNK_SIZE):
            for index, row in chunk.iterrows():
                data, error = process_row(row)
                if error:
                    failed_rows.append({"row": index, "error": error})
                else:
                    parsed_data.append(data)
            await process_batch.execute(parsed_data)
            parsed_data = []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Batch processed", "failed_rows": failed_rows}
