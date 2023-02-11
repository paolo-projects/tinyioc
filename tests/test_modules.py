import pytest

from tinyioc.helpers import IocContainer, register_instance, unregister_service, register_singleton, get_service, \
    unregister_module
from tinyioc.decorators import injectable, inject
from tinyioc.module.decorators import module
from tinyioc.ioc_exception import IocException
from tinyioc.module.module import IocModule, GlobalModule, FromModule
from tinyioc.module.provide import ProvideInstance, ProvideSingleton, ProvideTransient


def get_number():
    numbers = [15, 66, 134, 63, 711, 52, 22, 26, 91, 99, 55, 53]
    i = 0
    while True:
        yield numbers[i]
        i = (i + 1) % len(numbers)

@module()
class MyModule(IocModule):
    pass


class UnregisteredModule(IocModule):
    pass


def test_inject_module():
    @injectable(module=MyModule)
    class MyService:
        def test(self):
            return 1234

    called = False

    @inject(MyModule)
    def my_function(svc: MyService):
        nonlocal called
        assert svc.test() == 1234
        called = True

    my_function()
    assert called

    @inject()
    def global_module_function(svc: MyService):
        svc.test()

    # injecting from global module should not find any service
    with pytest.raises(TypeError):
        global_module_function()

    unregister_service(MyService, MyModule)


def test_specific_inject():
    class MyService:
        def __init__(self, number: int):
            self.num = number

        def test(self):
            return self.num

    register_instance(MyService(1234))
    register_instance(MyService(4321), MyModule)

    called = False

    @inject()
    def my_function(svc1: MyService = FromModule(GlobalModule), svc2: MyService = FromModule(MyModule)):
        nonlocal called
        assert svc1.test() == 1234
        assert svc2.test() == 4321
        called = True

    my_function()
    assert called


def test_module_not_registered():
    class MyService:
        def test(self):
            return 1010

    register_instance(MyService(), UnregisteredModule)

    called = False

    @inject()
    def test_function(svc: MyService):
        nonlocal called
        assert svc.test() == 1010
        called = True

    test_function()
    assert called

    unregister_service(MyService, UnregisteredModule)
    called = False

    register_singleton(MyService, UnregisteredModule)

    test_function()
    assert called

    svc = get_service(MyService, UnregisteredModule)
    assert svc is not None
    assert svc.test() == 1010

    with pytest.raises(IocException):
        IocContainer.get_instance().register_module(MyModule)

    unregister_module(MyModule)


def test_module_provides():
    class MyServiceA:
        def __init__(self, number: int):
            self.number = number

    class MyServiceB:
        def __init__(self):
            self.number = get_number()

    class MyServiceC:
        def __init__(self):
            self.number = get_number()

    @module()
    class MyModuleA(IocModule):
        provides = [
            ProvideInstance(MyServiceA(1515)),
            ProvideSingleton(MyServiceB),
            ProvideTransient(MyServiceC)
        ]

    numbers_b = []
    numbers_c = []

    @inject(MyModuleA)
    def test_function(svc_a: MyServiceA, svc_b: MyServiceB, svc_c: MyServiceC):
        assert svc_a.number == 1515
        numbers_b.append(svc_b.number)
        numbers_c.append(svc_c.number)

    for i in range(0, 5):
        test_function()

    assert len(numbers_b) == 5
    assert len(numbers_c) == 5

    for i in range(1, 5):
        assert numbers_b[i-1] == numbers_b[i]
        assert numbers_c[i-1] != numbers_c[i]
