from tinyioc.helpers import unregister_service, register_singleton
from tinyioc.decorators import injectable, inject
from tinyioc.types import ServiceLifetime


def rng_numbers():
    numbers = [0, 55, 18, 99, 10, 153, 795]
    i = 0
    while True:
        yield numbers[i]
        i = (i + 1) % len(numbers)


def test_function_injection():
    @injectable(ServiceLifetime.TRANSIENT)
    def rng_generator():
        return rng_numbers()

    results = []

    @inject()
    def my_fun(rng_number: rng_generator):
        nonlocal results
        results.append(rng_number)

    for i in range(0, 3):
        my_fun()

    assert len(results) == 3
    for i in range(1, 3):
        assert results[i] != results[i-1]


def test_generator_function():
    @injectable(ServiceLifetime.TRANSIENT)
    def gen_fun():
        yield rng_numbers()

    numbers = []

    @inject()
    def test_fun(generated: gen_fun):
        numbers.append(generated)

    for i in range(6):
        test_fun()

    assert len(numbers) == 6

    for i in range(1, 6):
        assert numbers[i] != numbers[i-1]

    numbers.clear()
    unregister_service(gen_fun)

    register_singleton(gen_fun)

    for i in range(6):
        test_fun()

    assert len(numbers) == 6

    for i in range(1, 6):
        assert numbers[i] == numbers[i-1]
