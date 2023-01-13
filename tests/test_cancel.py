import pytest
from async_iamport import HttpError, ResponseError


@pytest.mark.asyncio
async def test_cancel(iamport):
    with pytest.raises(TypeError):
        await iamport.cancel(imp_uid='nothing')
    with pytest.raises(ResponseError):
        await iamport.cancel('reason', imp_uid='nothing')
    try:
        await iamport.cancel('reason', imp_uid='nothing')
    except ResponseError as e:
        assert e.code == 1
        assert e.message == u'취소할 결제건이 존재하지 않습니다.'

#
# @pytest.mark.asyncio
# async def test_partial_cancel(iamport):
#     try:
#         await iamport.cancel('reason', imp_uid='nothing', amount=100)
#     except ResponseError as e:
#         assert e.code == 1
#         assert e.message == u'취소할 결제건이 존재하지 않습니다.'
#
#
# @pytest.mark.asyncio
# async def test_cancel_by_merchant_uid(iamport):
#     payload = {
#         'merchant_uid': 'any-merchant_uid',
#         'reason': 'any-reason',
#     }
#
#     try:
#         await iamport.cancel(**payload)
#     except ResponseError as e:
#         assert e.code == 1
#         assert e.message == u'취소할 결제건이 존재하지 않습니다.'
#
#
# @pytest.mark.asyncio
# async def test_cancel_without_merchant_uid(iamport):
#     payload = {
#         'merchant_uid': None,
#         'reason': 'any-reason',
#     }
#
#     try:
#         await iamport.cancel(**payload)
#     except KeyError as e:
#         assert 'merchant_uid or imp_uid is required' in str(e)
#
#
# @pytest.mark.asyncio
# async def test_cancel_by_merchant_uid_with_kwargs(iamport):
#     payload = {
#         'merchant_uid': 'any-merchant_uid',
#         'reason': 'any-reason',
#         'amount': 1234,
#     }
#
#     try:
#         await iamport.cancel(**payload)
#     except ResponseError as e:
#         assert e.code == 1
#         assert e.message == u'취소할 결제건이 존재하지 않습니다.'
#
#
# @pytest.mark.asyncio
# async def test_cancel_by_imp_uid(iamport):
#     payload = {
#         'imp_uid': 'any-imp_uid',
#         'reason': 'any-reason',
#     }
#
#     try:
#         await iamport.cancel(**payload)
#     except ResponseError as e:
#         assert e.code == 1
#         assert e.message == u'취소할 결제건이 존재하지 않습니다.'
