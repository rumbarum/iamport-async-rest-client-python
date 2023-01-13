import pytest

import async_iamport


@pytest.mark.asyncio
async def test_find_with_status(iamport):
    try:
        await iamport.find_by_merchant_uid(merchant_uid="1234qwer", status="cancelled")
    except async_iamport.HttpError as e:
        assert e.code == 404

    res = await iamport.find_by_merchant_uid(merchant_uid="1234qwer")
    assert res["merchant_uid"] == "1234qwer"

    res = await iamport.find_by_merchant_uid(merchant_uid="1234qwer", status="paid")
    assert res["merchant_uid"] == "1234qwer"
