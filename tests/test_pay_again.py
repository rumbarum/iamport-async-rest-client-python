import pytest

import async_iamport


@pytest.mark.asyncio
async def test_pay_again(iamport):
    # Without 'customer_uid'
    payload_notEnough = {
        "merchant_uid": "1234qwer",
        "amount": 5000,
    }

    try:
        await iamport.pay_again(**payload_notEnough)
    except KeyError as e:
        assert "Essential parameter is missing!: customer_uid" in str(e)

    payload_full = {
        "customer_uid": "00000000",
        "merchant_uid": "1234qwer",
        "amount": 5000,
    }

    try:
        await iamport.pay_again(**payload_full)
    except async_iamport.ResponseError as e:
        assert e.code == -1
