import pytest

from tinyioc.decorators import injectable, inject


@injectable()
class MyService:
    def test(self):
        return 1234


@pytest.mark.asyncio
async def test_async_inject():
    called = False

    @inject()
    async def my_fun(svc: MyService):
        nonlocal called
        assert svc.test() == 1234
        called = True

    await my_fun()
    assert called
