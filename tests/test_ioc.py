from typing import Optional

import pytest

from tinyioc.helpers import register_instance, register_singleton, register_transient, unregister_service,\
    get_service
from tinyioc.ioc_exception import IocException
from tinyioc.decorators import inject, injectable
from pytest import fixture


def get_number():
    numbers = [15, 66, 134, 63, 711, 52, 22, 26, 91, 99, 55, 53]
    i = 0
    while True:
        yield numbers[i]
        i = (i + 1) % len(numbers)


class Dummy:
    def __init__(self, number: Optional[float] = None) -> None:
        if number is not None:
            self.rng_num = number
        else:
            self.rng_num = get_number()

    def test(self):
        return 12345

    def get_rng(self):
        return self.rng_num


class AbstractDummy(object):
    def test(self) -> int:
        pass


@injectable(register_for=AbstractDummy)
class ConcreteDummy(AbstractDummy):
    _number: int

    def __init__(self, number: Optional[int] = None):
        self._number = number or 123

    def test(self) -> int:
        return self._number


@fixture()
def dummy_instance():
    dummy = Dummy(1.2345)
    register_instance(dummy)
    yield dummy
    unregister_service(Dummy)


@fixture()
def dummy_singleton():
    register_singleton(Dummy)
    yield None
    unregister_service(Dummy)


@fixture()
def dummy_oneshot():
    register_transient(Dummy)
    yield None
    unregister_service(Dummy)


class TestClass:
    def test_instance(self, dummy_instance):
        called = False

        @inject()
        def test_func(dummy: Dummy):
            nonlocal called
            assert dummy.test() == 12345
            assert dummy.get_rng() == 1.2345
            assert isinstance(dummy.get_rng(), float)
            called = True

        test_func()
        assert called

    def test_type(self, dummy_singleton):
        called = False

        @inject()
        def test_func(dummy: Dummy):
            nonlocal called
            assert dummy.test() == 12345
            called = True

        test_func()
        assert called

    def test_singleton(self, dummy_singleton):
        numbers = []
        called = False

        @inject()
        def test_func(dummy: Dummy):
            nonlocal called, numbers
            numbers.append(dummy.get_rng())
            called = True

        for i in range(0, 10):
            test_func()

        # In singleton scope, the service is instantiated once
        # so the number should be the same every time the function
        # is called and the service injected
        for i in range(1, len(numbers)):
            assert numbers[i - 1] == numbers[i]

        assert called

    def test_oneshot(self, dummy_oneshot):
        numbers = []
        called = False

        @inject()
        def test_func(dummy: Dummy):
            nonlocal called, numbers
            numbers.append(dummy.get_rng())
            called = True

        for i in range(0, 10):
            test_func()

        # In oneshot scope, every time we inject the service
        # it should be instantiated anew with a different number
        # (See the get_number() generator function above)
        for i in range(1, len(numbers)):
            assert numbers[i - 1] != numbers[i]

        assert called

    def test_service_existing(self, dummy_instance):
        with pytest.raises(IocException):
            register_singleton(Dummy)

    def test_service_existing_instance(self, dummy_instance):
        with pytest.raises(IocException):
            register_instance(Dummy())

    def test_no_service_found(self, dummy_instance):
        class SomeClass:
            pass

        svc = get_service(SomeClass)
        assert svc is None

    def test_no_service_found_injected(self, dummy_instance):
        class SomeClass:
            pass

        @inject()
        def test_func(no_service: SomeClass):
            pass

        with pytest.raises(TypeError):
            test_func()

    def test_interface(self):
        called = False

        @inject()
        def test_func(dummy: AbstractDummy):
            nonlocal called
            assert dummy.test() == 123
            called = True

        test_func()
        assert called
        unregister_service(AbstractDummy)

    def test_interface_2(self):
        register_singleton(ConcreteDummy, register_for=AbstractDummy, number=555)
        called = False

        @inject()
        def test_func(dummy: AbstractDummy):
            nonlocal called
            assert dummy.test() == 555
            called = True

        test_func()
        assert called

