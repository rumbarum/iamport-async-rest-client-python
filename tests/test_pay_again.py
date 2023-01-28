import async_iamport
import pytest


@pytest.mark.asyncio
async def test_pay_again(iamport):
    payload_full = {
        "customer_uid": "00000000",
        "merchant_uid": "1234qwer",
        "amount": 5000,
    }

    try:
        await iamport.pay_again(**payload_full)
    except async_iamport.ResponseError as e:
        assert e.code == -1
