import pytest
from pydantic import ValidationError

from src.routes.schema import BankslipRequest

def test_bankslip_request_valid(valid_bankslip_request):

    bankslip = BankslipRequest(**valid_bankslip_request)
    assert bankslip.name == "Elijah Santos"
    assert bankslip.government_id == "9558"
    assert bankslip.email == "janet95@example.com"
    assert bankslip.debt_amount == 7811
    assert bankslip.debt_id == "ea23f2ca-663a-4266-a742-9da4c9f4fcb3"


def test_bankslip_request_invalid_email(valid_bankslip_request):
    valid_bankslip_request['debt_amount'] = "a"

    with pytest.raises(ValidationError):
        BankslipRequest(**valid_bankslip_request)

