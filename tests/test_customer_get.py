import pytest

import async_iamport


@pytest.mark.asyncio
async def test_customer_get(iamport):
    customer_uid = "000000"
    with pytest.raises(async_iamport.ResponseError) as e:
        await iamport.customer_get(customer_uid)
        assert "요청하신 customer_uid(000000)로 등록된 정보를 찾을 수 없습니다." == e.message
