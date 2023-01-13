import pytest

import async_iamport


@pytest.mark.asyncio
async def test_find(iamport):
    with pytest.raises(KeyError):
        await iamport.find()
    with pytest.raises(async_iamport.HttpError):
        await iamport.find(imp_uid="test")
    with pytest.raises(async_iamport.HttpError):
        await iamport.find(merchant_uid="âàáaā")
