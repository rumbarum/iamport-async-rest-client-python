import async_iamport
import pytest


@pytest.mark.asyncio
async def test_pay_foreign(iamport):
    payload = {
        "merchant_uid": "uid",
        "amount": 100,
        "card_number": "card-number",
    }

    payload.update(
        {
            "expiry": "2016-08",
        }
    )

    try:
        await iamport.pay_foreign(**payload)
    except async_iamport.ResponseError as e:
        assert e.code == -1
