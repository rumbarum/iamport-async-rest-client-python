import pytest

import async_iamport


@pytest.mark.asyncio
async def test_is_paid_with_response(iamport):
    mocked_response = {
        "status": "paid",
        "amount": 1000,
    }
    assert True is await iamport.is_paid(
        amount=1000, response=mocked_response, merchant_uid="test"
    )


@pytest.mark.asyncio
async def test_is_paid_without_response(iamport):
    assert False is await iamport.is_paid(amount=1000, merchant_uid="qwer1234")
