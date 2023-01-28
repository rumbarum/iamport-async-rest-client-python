import json
from http import HTTPStatus
from socket import AF_INET
from typing import Any, Dict, Optional

import aiohttp
import arrow

IAMPORT_API_URL = "https://api.iamport.kr"
TOKEN_REFRESH_GAP = 60  # token 만료 1500s 정도
DEFAULT_TIMEOUT = 5
DEFAULT_POOL_SIZE = 100


class ResponseError(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message


class HttpError(Exception):
    def __init__(self, code: int, reason: str) -> None:
        self.code = code
        self.reason = reason


class AsyncIamport:
    """
    sync Iamport -> async Iamport
    """

    def __init__(
        self,
        *,
        imp_key: Optional[str] = None,
        imp_secret: Optional[str] = None,
        imp_url: str = IAMPORT_API_URL,
        pool_size: int = DEFAULT_POOL_SIZE,
        time_out: int = DEFAULT_TIMEOUT,
        token_refresh_gap: int = TOKEN_REFRESH_GAP,
    ) -> None:
        if imp_key is None or imp_secret is None:
            raise ValueError("IMP_KEY OR IMP_SECRET MISSED")
        self.imp_key = imp_key
        self.imp_secret = imp_secret
        self.imp_url = imp_url
        self.pool_size = pool_size
        self.time_out = time_out
        self.token_refresh_gap = token_refresh_gap
        self.token: Optional[str] = None
        self.token_expire: Optional[arrow.Arrow] = None
        self.session: Optional[aiohttp.ClientSession] = None

        self._init_session()

    def _init_session(self) -> None:
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.time_out)
            connector = aiohttp.TCPConnector(
                family=AF_INET, limit_per_host=self.pool_size
            )
            self.session = aiohttp.ClientSession(
                base_url=self.imp_url, timeout=timeout, connector=connector
            )

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def _get(self, url, payload=None) -> Dict:
        headers = await self._get_auth_headers()
        if self.session is not None:
            response = await self.session.get(url, headers=headers, params=payload)
            return await self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")

    async def _post(self, url, payload=None) -> Dict:
        headers = await self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        if self.session is not None:
            response = await self.session.post(
                url, headers=headers, data=json.dumps(payload)
            )
            return await self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")

    async def _put(self, url, payload=None) -> Dict[str, Any]:
        headers = await self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        if self.session is not None:
            response = await self.session.put(
                url, headers=headers, data=json.dumps(payload)
            )
            return await self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")

    async def _delete(self, url) -> Dict:
        headers = await self._get_auth_headers()
        if self.session is not None:
            response = await self.session.delete(url, headers=headers)
            return await self.get_response(response)
        else:
            raise ConnectionError("SESSION IS CLOSED")

    @staticmethod
    async def get_response(response) -> Dict:
        if response.status != HTTPStatus.OK:
            raise HttpError(response.status, response.reason)
        result = await response.json()
        if result["code"] != 0:
            raise ResponseError(result.get("code"), result.get("message"))
        return result.get("response")

    async def _get_auth_headers(self) -> Dict:
        return {"Authorization": await self._get_token()}

    async def _get_token(self) -> Optional[str]:
        if (
            self.token is not None
            and self.token_expire is not None
            and (self.token_expire - arrow.utcnow()).seconds > self.token_refresh_gap
        ):
            return self.token
        else:
            self.token = None
            url = "/users/getToken"
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
            timestamp: Optional[int] = resp.get("expired_at")
            if timestamp is not None:
                self.token_expire = arrow.Arrow.utcfromtimestamp(timestamp)
            self.token = resp.get("access_token")
            return self.token

    async def find_by_status(self, status: str, **params) -> Dict:
        """
        query payment history by status

        GET 'IAMPORT_API_URL/payments/status/{status}'

        :param status: ["all", "ready", "paid", "cancelled", "failed"]
        :param params: kwargs
        :return: result
        """

        url = f"/payments/status/{status}"
        return await self._get(url, payload=params)

    async def find_by_merchant_uid(
        self, merchant_uid: str, status: Optional[str] = None
    ) -> Dict:
        """
        query payment by merchant_uid and status(optional)

        GET 'IAMPORT_API_URL/payments/{merchant_uid}'
        or
        GET 'IAMPORT_API_URL/payments/{merchant_uid}/{status}'

        :param merchant_uid: merchant unique id
        :param status: ["ready", "paid", "cancelled", "failed"]
        :return: result
        """
        url = f"/payments/find/{merchant_uid}"
        if status is not None:
            url = f"{url}/{status}"
        return await self._get(url)

    async def find_by_imp_uid(self, imp_uid: str) -> Dict:
        """
        query payment by imp_uid

        GET 'IAMPORT_API_URL/payments/{imp_uid}'

        :param imp_uid: iamport unique id
        :return: result
        """
        url = f"/payments/{imp_uid}"
        return await self._get(url)

    async def find(self, **kwargs) -> Dict:
        """
        query payments  by merchant_uid or imp_uid

        :param kwargs: kwargs
        :return: result
        """
        merchant_uid = kwargs.get("merchant_uid")
        if merchant_uid:
            return await self.find_by_merchant_uid(merchant_uid)
        try:
            imp_uid = kwargs["imp_uid"]
        except KeyError:
            raise KeyError("merchant_uid or imp_uid is required")
        return await self.find_by_imp_uid(imp_uid)

    async def _cancel(self, payload: dict) -> Dict:
        """
        cancel payment

        POST 'IAMPORT_API_URL/payments/cancel'

        :param payload: payload
        :return: result
        """
        url = "/payments/cancel"
        return await self._post(url, payload)

    async def cancel_by_merchant_uid(
        self, merchant_uid: str, reason: str, **kwargs
    ) -> Dict:
        """
        cancel payment by merchant_uid

        POST 'IAMPORT_API_URL/payments/cancel'

        :param merchant_uid: merchant unique id
        :param reason: reason for cancel
        :param kwargs: keyword arguments
        :return: result
        """

        payload = {"merchant_uid": merchant_uid, "reason": reason}
        if kwargs:
            payload.update(kwargs)
        return await self._cancel(payload)

    async def cancel_by_imp_uid(self, imp_uid: str, reason: str, **kwargs) -> Dict:
        """
        cancel payment by imp_uid

        POST 'IAMPORT_API_URL/payments/cancel'

        :param imp_uid: iamport unique id
        :param reason: reason for cancel
        :param kwargs: keyword arguments
        :return:
        """
        payload = {"imp_uid": imp_uid, "reason": reason}
        if kwargs:
            payload.update(kwargs)
        return await self._cancel(payload)

    async def cancel(self, reason: str, **kwargs) -> Dict:
        """
        cancel payment by merchant_uid or imp_uid

        POST 'IAMPORT_API_URL/payments/cancel'

        :param reason: reason for cancel
        :param kwargs: keyword arguments
        :return: result
        """
        imp_uid = kwargs.pop("imp_uid", None)
        if imp_uid:
            return await self.cancel_by_imp_uid(imp_uid, reason, **kwargs)

        merchant_uid = kwargs.pop("merchant_uid", None)
        if merchant_uid is None:
            raise KeyError("merchant_uid or imp_uid is required")
        return await self.cancel_by_merchant_uid(merchant_uid, reason, **kwargs)

    async def is_paid(self, amount: float, **kwargs) -> bool:
        """
        check that payment is paid

        :param amount: payment value
        :param kwargs: keyword arguments
        :return:
        """
        response = kwargs.get("response")
        if not response:
            response = await self.find(**kwargs)
        status = response.get("status")
        response_amount = response.get("amount")
        return status == "paid" and response_amount == amount

    async def pay_onetime(self, **kwargs) -> Dict:
        """
        payments once only with card information

        POST 'IAMPORT_API_URL/subscribe/payments/onetime'

        :param kwargs: keyword arguments
        :return: result
        """
        url = "/subscribe/payments/onetime"

        return await self._post(url, kwargs)

    async def pay_again(self, **kwargs) -> Dict:
        """
        payment again with saved billing key

        POST 'IAMPORT_API_URL/subscribe/payments/again'

        :param kwargs: keyword arguments
        :return: result
        """
        url = "/subscribe/payments/again"

        return await self._post(url, kwargs)

    async def pay_foreign(self, **kwargs) -> Dict:
        """
        depreciated

        :param kwargs:
        :return:
        """
        url = "/subscribe/payments/foreign"

        return await self._post(url, kwargs)

    async def pay_schedule(self, **kwargs) -> Dict:
        """
        register scheduled payment

        POST 'IAMPORT_API_URL/subscribe/payments/schedule'

        :param kwargs: keyword arguments
        :return: result
        """

        headers = await self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        url = "/subscribe/payments/schedule"

        return await self._post(url, kwargs)

    async def pay_schedule_get(self, merchant_uid: str) -> Dict:
        """
        query scheduled payment by merchant_uid

        GET 'IAMPORT_API_URL/subscribe/payments/schedule/{merchant_uid}

        :param merchant_uid: merchant unique id
        :return: result
        """
        url = f"/subscribe/payments/schedule/{merchant_uid}"
        return await self._get(url)

    async def pay_schedule_get_between(self, **kwargs) -> Dict:
        """
        query scheduled payment by datetime range

        GET 'IAMPORT_API_URL/subscribe/payments/schedule'

        :param kwargs: keyword arguments
        :return: result
        """
        url = f"/subscribe/payments/schedule"

        return await self._get(url, kwargs)

    async def pay_unschedule(self, **kwargs) -> Dict:
        """
        cancel scheduled payment

        POST 'IAMPORT_API_URL/subscribe/payments/unschedule'

        :param kwargs: keyword arguments
        :return: result
        """
        url = f"/subscribe/payments/unschedule"

        return await self._post(url, kwargs)

    async def customer_create(self, **kwargs) -> Dict:
        """
        create customer billing key

        POST 'IAMPORT_API_URL/subscribe/customers/{customer_uid}'

        :param kwargs: keyword arguments
        :return: result
        """
        customer_uid = kwargs.get("customer_uid")
        url = f"/subscribe/customers/{customer_uid}"

        return await self._post(url, kwargs)

    async def customer_get(self, customer_uid: str) -> Dict:
        """
        query customer billing key

        GET 'IAMPORT_API_URL/subscribe/customers/{customer_uid}'

        :param customer_uid: customer's payment method unique id
        :return: result
        """
        url = f"/subscribe/customers/{customer_uid}"
        return await self._get(url)

    async def customer_delete(self, customer_uid: str) -> Dict:
        """
        delete customer billing key

        DELETE 'IAMPORT_API_URL/subscribe/customers/{customer_uid}'

        :param customer_uid: customer's payment method unique id
        :return: result
        """
        url = f"/subscribe/customers/{customer_uid}"
        return await self._delete(url)

    async def prepare(self, merchant_uid: str, amount: float) -> Dict:
        """
        register payment amount with uid in advance for safety
        '/payments/prepare'

        :param merchant_uid: merchant unique id
        :param amount: amount
        :return: result
        """
        url = "/payments/prepare"
        payload = {"merchant_uid": merchant_uid, "amount": amount}
        return await self._post(url, payload)

    async def prepare_validate(self, merchant_uid: str, amount: float) -> bool:
        """
        validate payment amount with uid on registered payment
        '/payments/prepare/{merchant_uid}'

        :param merchant_uid: merchant unique id
        :param amount: amount
        :return: result
        """
        url = f"/payments/prepare/{merchant_uid}"
        response = await self._get(url)
        response_amount = response.get("amount")
        return response_amount == amount

    async def adjust_prepare_amount(
        self, merchant_uid: str, amount: float
    ) -> Dict[str, Any]:
        """
        adjust amount of pre-registered payment

        PUT 'IAMPORT_API_URL/payments/prepare'

        :param merchant_uid: merchant unique id
        :param amount: amount
        :return: result
        """
        url = f"/payments/prepare"
        payload = {"merchant_uid": merchant_uid, "amount": amount}
        return await self._put(url, payload=payload)

    async def revoke_vbank_by_imp_uid(self, imp_uid) -> Dict:
        url = f"/vbanks/{imp_uid}"
        return await self._delete(url)

    async def find_certification(self, imp_uid: str) -> Dict:
        """
        query sms authentication result

        GET 'IAMPORT_API_URL/certifications/{imp_uid}'

        :param imp_uid: imp_uid
        :return: result
        """
        url = f"/certifications/{imp_uid}"
        return await self._get(url)

    async def cancel_certification(self, imp_uid: str) -> Dict:
        """
        delete sms authentication result

        DELETE 'IAMPORT_API_URL/certifications/{imp_uid}'

        :param imp_uid: imp_uid
        :return: result
        """

        url = f"/certifications/{imp_uid}"
        return await self._delete(url)

    async def init_otp_certification(self, **kwargs) -> Dict:
        """
        init otp authentication through sms with personal information

        POST 'IAMPORT_API_URL/certifications/otp/request'

        :return: result
        """

        url = f"/certifications/otp/request"
        return await self._post(url, payload=kwargs)

    async def confirm_otp_certification(self, imp_uid: str, **kwargs) -> Dict:
        """
        complete otp authentication through sms with personal information

        POST 'IAMPORT_API_URL/certifications/otp/confirm/{imp_uid}'

        :return: result
        """

        url = f"/certifications/otp/confirm/{imp_uid}"
        return await self._post(url, payload=kwargs)
