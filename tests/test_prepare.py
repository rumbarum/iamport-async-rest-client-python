import random
import string

import pytest


@pytest.mark.asyncio
async def test_prepare(iamport):
    amount = 12000
    mid = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
    )
    result = await iamport.prepare(merchant_uid=mid, amount=amount)
    assert result["amount"] == amount
    assert result["merchant_uid"] == mid

    result = await iamport.prepare_validate(merchant_uid=mid, amount=amount)
    assert result
