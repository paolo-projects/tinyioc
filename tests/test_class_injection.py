import pytest

from tinyioc.helpers import register_singleton, register_instance, unregister_service
from tinyioc.decorators import inject, injectable
from tinyioc.types import ServiceLifetime


def generate_number():
    nums = [0, 55, 96, 10, 474, 6594, 134, 9873, 123748, 142, 456]
    i = 0
    while True:
        yield nums[i]
        i = (i + 1) % len(nums)


class Dummy:
    def test(self):
        return 12345


class SomeClass:
    has_injected: bool

    @inject()
    def __init__(self, dummy: Dummy):
        self.has_injected = dummy.test() == 12345


def test_class():
    register_instance(Dummy())
    cls = SomeClass()

    assert cls.has_injected
    unregister_service(Dummy)


def test_inject():
    register_singleton(Dummy)
    register_singleton(SomeClass)

    called = False

    @inject()
    def test_method(test_cls: SomeClass):
        nonlocal called
        assert test_cls.has_injected
        called = True

    test_method()
    assert called

    unregister_service(Dummy)
    unregister_service(SomeClass)


def test_injectable():
    @injectable()
    class MyClass:
        def __init__(self):
            self.num = generate_number()

        def test(self):
            return self.num

    numbers = []

    @inject()
    def my_function(my_class: MyClass):
        nonlocal numbers
        numbers.append(my_class.test())

    for i in range(0, 5):
        my_function()
    assert len(numbers) == 5

    for i in range(1, len(numbers)):
        assert(numbers[i] == numbers[i-1])

    unregister_service(MyClass)

    with pytest.raises(TypeError):
        my_function()


def test_injectable_oneshot():
    @injectable(ServiceLifetime.TRANSIENT)
    class MyClass:
        def __init__(self):
            self.num = generate_number()

        def test(self):
            return self.num

    numbers = []

    @inject()
    def my_function(my_class: MyClass):
        nonlocal numbers
        numbers.append(my_class.test())

    for i in range(0, 5):
        my_function()
    assert len(numbers) == 5

    for i in range(1, len(numbers)):
        assert(numbers[i] != numbers[i-1])

    unregister_service(MyClass)

    with pytest.raises(TypeError):
        my_function()
