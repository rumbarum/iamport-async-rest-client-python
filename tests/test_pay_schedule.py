import time

import async_iamport
import pytest


@pytest.mark.asyncio
async def test_pay_schedule(iamport):
    schedule_at = int(time.time() + 1000)
    payload_full = {
        "customer_uid": "00000000",
        "schedules": [
            {
                "merchant_uid": "pay_schedule_%s" % str(time.time()),
                "schedule_at": schedule_at,
                "amount": 5000,
                "name": "주문명",
                "buyer_name": "주문자명",
                "buyer_email": "주문자 Email주소",
                "buyer_tel": "주문자 전화번호",
                "buyer_addr": "주문자 주소",
                "buyer_postcode": "주문자 우편번호",
            },
        ],
    }

    try:
        await iamport.pay_schedule(**payload_full)
    except async_iamport.ResponseError as e:
        assert e.code == 1
        assert "등록된 고객정보가 없습니다." in e.message
