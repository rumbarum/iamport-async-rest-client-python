# IAMPORT async python rest client

from https://github.com/iamport/iamport-rest-client-python

## 개선 사항
1. Token 재사용
2. sync -> async
3. .format -> f-string
4. typing 적용, mypy 적용


## 작업 예정
1. 필수 필드 검증을 아에 제거하고 iamport api 의 응답만 확인하도록 해서 필드 변경에 대한 유연성 및 코드의 책임 범위를 낮추기
2. 함수들의 이름을 iamport api들의 호출 이름과 유사하게 전부 정리하기
3. 미구현 API 추가 예정

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
