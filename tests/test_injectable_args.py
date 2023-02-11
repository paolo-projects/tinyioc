from tinyioc.decorators import injectable, inject
from tinyioc.helpers import unregister_service
from tinyioc.container import IocContainer
from tinyioc.module.decorators import module
from tinyioc.module.module import IocModule


def test_instance_named():
    @injectable(n1=12345, n2=67890)
    class MyClass:
        def __init__(self, n1, n2):
            self.n1 = n1
            self.n2 = n2

        def test(self):
            return self.n1, self.n2

    called = False

    @inject()
    def test_fun(svc: MyClass):
        nonlocal called
        assert svc.test() == (12345, 67890)
        called = True

    test_fun()
    assert called
    unregister_service(MyClass)


def test_instance_module():
    @module()
    class MyModule(IocModule):
        pass

    @injectable(module=MyModule, n1=12345, n2=67890)
    class MyClass:
        def __init__(self, n1, n2):
            self.n1 = n1
            self.n2 = n2

        def test(self):
            return self.n1, self.n2

    called = False

    @inject(MyModule)
    def test_fun(svc: MyClass):
        nonlocal called
        assert svc.test() == (12345, 67890)
        called = True

    test_fun()
    assert called
    unregister_service(MyClass)
    IocContainer.get_instance().unregister_module(MyModule)


def test_instance_late_params():
    def get_config():
        return {
            "n1": 12345,
            "n2": 67890
        }

    @injectable(n1=get_config()["n1"], n2=get_config()["n2"])
    class MyClass:
        def __init__(self, n1, n2):
            self.n1 = n1
            self.n2 = n2

        def test(self):
            return self.n1, self.n2

    called = False

    @inject()
    def test_fun(svc: MyClass):
        nonlocal called
        assert svc.test() == (12345, 67890)
        called = True

    test_fun()
    assert called
    unregister_service(MyClass)
