import pytest
from pydantic import ValidationError

from src.routes.schema import BankslipDTO

def test_bankslip_request_valid(valid_bankslip_request):
    valid_bankslip_request["bankslip_file"] = "fake_file"
    valid_bankslip_request["propagated"] = True

    bankslip = BankslipDTO(**valid_bankslip_request)
    assert bankslip.name == "Elijah Santos"
    assert bankslip.government_id == "9558"
    assert bankslip.email == "janet95@example.com"
    assert bankslip.debt_amount == 7811
    assert bankslip.propagated == True


def test_bankslip_request_invalid_email(valid_bankslip_request):
    valid_bankslip_request['debt_amount'] = "a"

    with pytest.raises(ValidationError):
        BankslipDTO(**valid_bankslip_request)

