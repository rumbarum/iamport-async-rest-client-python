## v0.2.0 (2023-01-28)

### Feat

- **/payments/prepare**: PUT mehtod: adjust_prepare_amount
- instance method: _put for PUT request
- otp certification method

### Refactor

- **func-pay_schedule_get**: change parameter name merchant_id -> merchant_uid
- **/subscribe/payments/**: delete key validation
- **/subscribe/**: add type annotations and docstring
- **/payments/**: add type annotation and docstring
- **/payments/status/**: add docstring
- **/payments/prepare**: add type annotation and docstring
- add type annotation and docs on function related /certification
- delete empty workflow.yml

## v0.1.1 (2023-01-18)

### Fix

- **client.py**: fix TOKEN_REFRESH_GAP 120 -> 60

### Refactor

- _get_user code block
- formatting using mypy
- formatting using isort

## v0.1.0 (2023-01-14)

### Feat

- sync rest client -> async rest client
