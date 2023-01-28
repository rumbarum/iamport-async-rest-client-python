import arrow
import pytest


@pytest.mark.asyncio
async def test_token_renewed_when_expire_is_under_60s(iamport):
    """
    given
        iamport client with new token
    when
        set token_expire < 60s
    then
        token expire is renewed as token set again
    """
    await iamport._get_token()
    pre_token_expire = iamport.token_expire
    now = arrow.utcnow()
    iamport.token_expire = now.shift(seconds=30)
    await iamport._get_token()
    post_token_expire = iamport.token_expire
    assert pre_token_expire == post_token_expire
