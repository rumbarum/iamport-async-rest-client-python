from socket import AF_INET
from typing import List, Optional, Dict

import aiohttp
import json
from http import HTTPStatus
from datetime import datetime

IAMPORT_API_URL = "https://api.iamport.kr"
VALID_TOKEN_GAP = 60
DEFAULT_TIMEOUT = 5
DEFAULT_POOL_SIZE = 100


class ResponseError(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message


class HttpError(Exception):
    def __init__(self, code:int, reason: str) -> None:
        self.code = code
        self.reason = reason


class AiohttpSession:
    def __init__(
        self,
        *,
        imp_key: Optional[str] = None,
        imp_secret: Optional[str] = None,
        imp_url: str = IAMPORT_API_URL,
        pool_size: int = DEFAULT_POOL_SIZE,
        time_out: int = DEFAULT_TIMEOUT,
    ) -> None:
        if imp_key is None or imp_secret is None:
            raise ValueError("IMP_KEY OR IMP_SECRET MISSED")
        self.imp_key = imp_key
        self.imp_secret = imp_secret
        self.imp_url = imp_url
        self.pool_size = pool_size
        self.time_out = time_out
        self.token: Optional[str] = None
        self.token_expire: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None

    def get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.time_out)
            connector = aiohttp.TCPConnector(
                family=AF_INET, limit_per_host=self.pool_size
            )
            self.session = aiohttp.ClientSession(
                base_url=self.imp_url, timeout=timeout, connector=connector
            )
        return self.session

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def on_startup(self) -> None:
        self.get_session()

    async def on_shutdown(self) -> None:
        await self.close_session()

    async def _get(self, url, payload=None) -> Dict:
        headers = await self.get_auth_headers()
        if self.session is not None:
            response = await self.session.get(url, headers=headers, params=payload)
            return self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")

    async def _post(self, url, payload=None) -> Dict:
        headers = await self.get_auth_headers()
        headers["Content-Type"] = "application/json"
        if self.session is not None:
            response = await self.session.post(
                url, headers=headers, data=json.dumps(payload)
            )
            return self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")


    async def _delete(self, url) -> Dict:
        headers = await self.get_auth_headers()
        if self.session is not None:
            response = await self.session.delete(url, headers=headers)
            return self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")

    async def get_auth_headers(self) -> Dict:
        return {"Authorization": await self._get_token()}

    async def _get_token(self) ->  Optional[str]:
        if (
            self.token is not None
            and self.token_expire is not None
            and (self.token_expire - datetime.utcnow()).total_seconds()
            > VALID_TOKEN_GAP
        ):
            return self.token
        else:
            self.token = None
            url = f"/users/getToken"
            payload = {"imp_key": self.imp_key, "imp_secret": self.imp_secret}
            if self.session is not None:
                response = await self.session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                )
            else:
                raise ConnectionError("SESSION IS CLOSED")
        resp = await self.get_response(response)
        timestamp = resp.get("expired_at")
        if timestamp is not None:
            timestamp_float = float(timestamp)
            self.token_expire = datetime.fromtimestamp(timestamp_float)
        self.token = resp.get("access_token")
        return self.token

    @staticmethod
    async def get_response(response) -> Dict:
        if response.status != HTTPStatus.OK:
            raise HttpError(response.status, response.reason)
        result = await response.json()
        if result["code"] != 0:
            raise ResponseError(result.get("code"), result.get("message"))
        return result.get("response")

    async def find_by_status(self, status, **params) -> Dict:
        url = f"/payments/status/{status}"
        return await self._get(url, payload=params)

    async def find_by_merchant_uid(self, merchant_uid, status=None) -> Dict:
        url = f"/payments/find/{merchant_uid}"
        if status is not None:
            url = f"/{status}"
        return await self._get(url)

    async def find_by_imp_uid(self, imp_uid) -> Dict:
        url = f"/payments/{imp_uid}"
        return await self._get(url)

    async def find(self, **kwargs) -> Dict:
        merchant_uid = kwargs.get("merchant_uid")
        if merchant_uid:
            return await self.find_by_merchant_uid(merchant_uid)
        try:
            imp_uid = kwargs["imp_uid"]
        except KeyError:
            raise KeyError("merchant_uid or imp_uid is required")
        return await self.find_by_imp_uid(imp_uid)

    async def _cancel(self, payload) -> Dict:
        url = f"/payments/cancel"
        return await self._post(url, payload)

    async def pay_onetime(self, **kwargs) -> Dict:
        url = f"/subscribe/payments/onetime"
        for key in [
            "merchant_uid",
            "amount",
            "card_number",
            "expiry",
            "birth",
            "pwd_2digit",
        ]:
            if key not in kwargs:
                raise KeyError("Essential parameter is missing!: %s" % key)

        return await self._post(url, kwargs)

    async def pay_again(self, **kwargs) -> Dict:
        url = f"/subscribe/payments/again"
        for key in ["customer_uid", "merchant_uid", "amount"]:
            if key not in kwargs:
                raise KeyError("Essential parameter is missing!: %s" % key)

        return await self._post(url, kwargs)

    async def customer_create(self, **kwargs) -> Dict:
        customer_uid = kwargs.get("customer_uid")
        for key in ["customer_uid", "card_number", "expiry", "birth"]:
            if key not in kwargs:
                raise KeyError("Essential parameter is missing!: %s" % key)
        url = f"/subscribe/customers/{customer_uid}"
        return await self._post(url, kwargs)

    async def customer_get(self, customer_uid) -> Dict:
        url = f"/subscribe/customers/{customer_uid}"
        return await self._get(url)

    async def customer_delete(self, customer_uid) -> Dict:
        url = f"/subscribe/customers/{customer_uid}"
        return await self._delete(url)

    async def pay_foreign(self, **kwargs) -> Dict:
        url = f"/subscribe/payments/foreign"
        for key in ["merchant_uid", "amount", "card_number", "expiry"]:
            if key not in kwargs:
                raise KeyError("Essential parameter is missing!: %s" % key)

        return await self._post(url, kwargs)

    async def pay_schedule(self, **kwargs) -> Dict:
        headers = await self.get_auth_headers()
        headers["Content-Type"] = "application/json"
        url = f"/subscribe/payments/schedule"
        if "customer_uid" not in kwargs:
            raise KeyError("customer_uid is required")
        for key in ["merchant_uid", "schedule_at", "amount"]:
            for schedules in kwargs["schedules"]:
                if key not in schedules:
                    raise KeyError("Essential parameter is missing!: %s" % key)

        return await self._post(url, kwargs)

    async def pay_schedule_get(self, merchant_id) -> Dict:
        url = f"/subscribe/payments/schedule/{merchant_id}"
        return await self._get(url)

    async def pay_schedule_get_between(self, **kwargs) -> Dict:
        url = f"/subscribe/payments/schedule"
        for key in ["schedule_from", "schedule_to"]:
            if key not in kwargs:
                raise KeyError("Essential parameter is missing!: %s" % key)

        return await self._get(url, kwargs)

    async def pay_unschedule(self, **kwargs) -> Dict:
        url = f"/subscribe/payments/unschedule"
        if "customer_uid" not in kwargs:
            raise KeyError("customer_uid is required")

        return await self._post(url, kwargs)

    async def cancel_by_merchant_uid(self, merchant_uid, reason, **kwargs) -> Dict:
        payload = {"merchant_uid": merchant_uid, "reason": reason}
        if kwargs:
            payload.update(kwargs)
        return await self._cancel(payload)

    async def cancel_by_imp_uid(self, imp_uid, reason, **kwargs) -> Dict:
        payload = {"imp_uid": imp_uid, "reason": reason}
        if kwargs:
            payload.update(kwargs)
        return await self._cancel(payload)

    async def cancel(self, reason, **kwargs) -> Dict:
        imp_uid = kwargs.pop("imp_uid", None)
        if imp_uid:
            return await self.cancel_by_imp_uid(imp_uid, reason, **kwargs)

        merchant_uid = kwargs.pop("merchant_uid", None)
        if merchant_uid is None:
            raise KeyError("merchant_uid or imp_uid is required")
        return await self.cancel_by_merchant_uid(merchant_uid, reason, **kwargs)

    async def is_paid(self, amount, **kwargs) -> bool:
        response = kwargs.get("response")
        if not response:
            response = await self.find(**kwargs)
        status = response.get("status")
        response_amount = response.get("amount")
        return status == "paid" and response_amount == amount

    async def prepare(self, merchant_uid, amount) -> Dict:
        url = f"/payments/prepare"
        payload = {"merchant_uid": merchant_uid, "amount": amount}
        return await self._post(url, payload)

    async def prepare_validate(self, merchant_uid, amount) -> bool:
        url = f"/payments/prepare/{merchant_uid}"
        response = await self._get(url)
        response_amount = response.get("amount")
        return response_amount == amount

    async def revoke_vbank_by_imp_uid(self, imp_uid) -> Dict:
        url = f"/vbanks/{imp_uid}"
        return await self._delete(url)

    async def find_certification(self, imp_uid) -> Dict:
        url = f"/certifications/{imp_uid}"
        return await self._get(url)

    async def cancel_certification(self, imp_uid) -> Dict:
        url = f"/certifications/{imp_uid}"
        return await self._delete(url)
