# IAMPORT async python rest client

from https://github.com/iamport/iamport-rest-client-python

## 개선 사항
1. sync -> async
2. Token 재사용
   - 만료 60s 이상 남았을 경우 재사용
   - 그 이하일 경우 재인증
3. .format() -> f-string
4. typing 적용, mypy 적용


## 변경 사항
1. python2 지원 안함
2. requests -> aiohttp
3. 기존 retry(3회) 옵션 제거

## 작업 예정
1. 필수 필드 검증을 아에 제거하고 iamport api 의 응답만 확인하도록 해서 필드 변경에 대한 유연성 및 코드의 책임 범위를 낮추기
   - 기존 method 호환을 위해 유지
   - 추가 API는 path parameter 만 positional args 으로 처리, 나머지는 kwargs로 payload 담음
2. ~~함수들의 이름을 iamport api들의 호출 이름과 유사하게 전부 정리하기~~
   - 기존 client api 유지
3. 미구현 API 추가 예정
   - param validation 제거
   - type annotation 추가
   - docstring 추가

## 주의 사항
- 사용 중 발생한 문제의 책임은 사용자에게 있습니다.
- iamport 정식 api로 동작 완전성 테스트 되지 않았습니다. url 이상 여부만 검증 되었습니다.


## Deps

- python >= 3.7

- Aiohttp >= 3.8.3
- arrow >= 1.2.3


## Install

```commandline
pip install async-iamport
```

## FastAPI Example

```python
from fastapi import FastAPI

from async_iamport import AsyncIamport

DEFAULT_TEST_IMP_KEY = "imp_apikey"
DEFAULT_TEST_IMP_SECRET = (
    "ekKoeW8RyKuT0zgaZsUtXXTLQ4AhPFW3ZGseDA6b"
    "kA5lamv9OqDMnxyeB9wqOsuO9W3Mx9YSJ4dTqJ3f"
)

async_iamport = AsyncIamport(
    imp_key=DEFAULT_TEST_IMP_KEY, imp_secret=DEFAULT_TEST_IMP_SECRET
)

app = FastAPI(on_shutdown=[async_iamport.close_session])


mocked_response = {
    "status": "paid",
    "amount": 1000,
}

@app.get("/")
async def root():
    return await async_iamport.find_by_merchant_uid(merchant_uid="1234qwer")
```
```commandline
uvicorn main:app --reload
``` 
