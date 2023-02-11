from tinyioc.helpers import unregister_service
from tinyioc.decorators import inject_getter, inject, injectable


@injectable()
class ServiceA:
    def test(self):
        return 6789


def test_inject_getter():
    @injectable()
    class ServiceB:
        @inject_getter()
        def get_service_a(self) -> ServiceA:
            pass

    called = False

    @inject()
    def test_function(service_b: ServiceB):
        nonlocal called
        assert service_b.get_service_a().test() == 6789
        called = True

    test_function()
    assert called
    unregister_service(ServiceB)


def test_bad_inject_getter_fn():
    @injectable()
    class ServiceB:
        @inject_getter()
        def get_service_a(self):
            # This function has no return type and can't be injected
            pass
    called = False

    @inject()
    def test_function(service_b: ServiceB):
        nonlocal called
        assert service_b.get_service_a() is None
        called = True

    test_function()
    assert called
