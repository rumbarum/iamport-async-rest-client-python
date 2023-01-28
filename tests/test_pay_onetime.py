import random
import string

import async_iamport
import pytest


@pytest.mark.asyncio
async def test_pay_onetime(iamport):
    merchant_uid = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
    )

    merchant_uid = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
    )

    payload_full = {
        "merchant_uid": merchant_uid,
        "amount": 5000,
        "card_number": "4092-0230-1234-1234",
        "expiry": "2019-03",
        "birth": "500203",
        "pwd_2digit": "19",
    }

    try:
        await iamport.pay_onetime(**payload_full)
    except async_iamport.ResponseError as e:
        assert e.code == -1
        assert "카드정보 인증에 실패하였습니다." in e.message
