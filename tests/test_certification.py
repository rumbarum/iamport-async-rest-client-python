import pytest

import async_iamport


@pytest.mark.asyncio
async def test_find_certification(iamport):
    imp_uid = "imp_12341234"

    with pytest.raises(async_iamport.HttpError) as e:
        await iamport.find_certification(imp_uid)
        assert "인증결과가 존재하지 않습니다." == e.message

    with pytest.raises(async_iamport.HttpError) as e:
        await iamport.cancel_certification(imp_uid)
        assert "인증결과가 존재하지 않습니다." == e.message
