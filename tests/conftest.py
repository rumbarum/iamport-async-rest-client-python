from pytest import fixture
import asyncio
import pytest
import pytest_asyncio
from async_iamport import AiohttpSession

DEFAULT_TEST_IMP_KEY = 'imp_apikey'
DEFAULT_TEST_IMP_SECRET = (
    'ekKoeW8RyKuT0zgaZsUtXXTLQ4AhPFW3ZGseDA6b'
    'kA5lamv9OqDMnxyeB9wqOsuO9W3Mx9YSJ4dTqJ3f'
)


def pytest_addoption(parser):
    parser.addoption(
        '--imp-key',
        default=DEFAULT_TEST_IMP_KEY,
        help='iamport client key for testing [default: %(default)s]'
    )
    parser.addoption(
        '--imp-secret',
        default=DEFAULT_TEST_IMP_SECRET,
        help='iamport secret key for testing [default: %(default)s]'
    )

@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def iamport(request):
    imp_key = request.config.getoption('--imp-key')
    imp_secret = request.config.getoption('--imp-secret')
    session = AiohttpSession(imp_key=imp_key, imp_secret=imp_secret)
    session.get_session()
    yield session
    await session.close_session()
