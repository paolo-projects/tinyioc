from typing import TypeVar, Type, Dict, List
from .provide import Provide
from ..service_entry import ServiceEntry

T = TypeVar("T")


class IocModule:
    """
    Base class for a module. All modules must inherit from this class
    """
    services: Dict[Type[T], ServiceEntry[T]]

    provides: List[Provide]

    def __init__(self):
        self.services = {}


class GlobalModule(IocModule):
    pass


E = TypeVar("E", bound=IocModule)


class FromModule:
    """
    Helper class to define the module from which a dependency is injected

    Example:

     .. code-block::
     
        @inject()
        def my_fun(dep_a: DependencyA = FromModule(ModuleA), dep_b: DependencyB = FromModule(ModuleB)):
            ...
    """
    def __init__(self, module: Type[E]):
        self.module = module
