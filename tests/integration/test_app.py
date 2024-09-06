import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport
from json import loads


@pytest.mark.anyio(backend="asyncio")
class TestBankslipAPI:
    async def test_validation_errors(self, application, valid_bankslip_request):
        body = valid_bankslip_request
        field_to_remove = "debt_id"
        del body[field_to_remove]
        async with AsyncClient(
            transport=ASGITransport(app=application),
            base_url="http://testserver",
        ) as client:
            response = await client.post("/bankslip", json=body)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            response_text = loads(response.text)
            assert response_text["detail"][0]["loc"][1] == field_to_remove
