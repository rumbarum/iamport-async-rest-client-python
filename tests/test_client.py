import pytest

import async_iamport


@pytest.mark.asyncio
async def test_init_otp_certification(iamport):
    user_info = {
        "name": "김유저",
        "phone": "010-1234-1234",
        "birth": "2000-10-10",
        "gender_digit": "1",
        "carrier": "SKT",
        "is_mvno": False,
        "company": "coop",
    }

    with pytest.raises(async_iamport.HttpError) as e:
        await iamport.init_otp_certification(**user_info)
        assert e.code == 400


@pytest.mark.asyncio
async def test_confirm_otp_certification(iamport):
    payload = {"imp_uid": "123456", "otp": "123456"}
    with pytest.raises(async_iamport.HttpError) as e:
        await iamport.confirm_otp_certification(**payload)
        assert e.code == 400


@pytest.mark.asyncio
async def test_adjust_prepare_amount(iamport):
    payload = {"merchant_uid": "123456", "amount": "123456"}
    with pytest.raises(async_iamport.HttpError) as e:
        await iamport.adjust_prepare_amount(**payload)
        assert e.code == 400
