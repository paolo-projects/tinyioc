from typing import Optional, Type, TypeVar, Dict

from .module.module import IocModule, GlobalModule
from .service_entry import ServiceEntry
from .ioc_exception import IocException
from .types import ServiceLifetime

T = TypeVar('T')
K= TypeVar('K')
E = TypeVar('E', bound=IocModule)


class IocContainer:
    """
    The IOC container class
    """

    __instance: "IocContainer" = None
    __modules: Dict[Type[E], E]

    def __init__(self):
        """
        Create a new instance of the IocContainer. This class is supposed to be a singleton object,
        so you should never instantiate it by yourself
        """
        self.__modules = {
            GlobalModule: GlobalModule()
        }

    @staticmethod
    def get_instance() -> 'IocContainer':
        """
        Get the Ioc container singleton instance

        :return: The singleton IocContainer instance
        :return-type: IocContainer
        """
        if IocContainer.__instance is None:
            IocContainer.__instance = IocContainer()
        return IocContainer.__instance

    def register_instance(self, instance: T, module: Type[E] = GlobalModule, register_for: Optional[Type[K]] = None) -> None:
        """
        Register a service through the instance provided (singleton scope)

        :param instance: The service instance
        :param module: The module to register the service into
        :param register_for: The class-interface to register this instance for
        """
        if module not in self.__modules:
            module = GlobalModule

        module_instance = self.__modules[module]
        cls_type = instance.__class__
        if register_for:
            cls_type = register_for

        if cls_type not in module_instance.services:
            entry: ServiceEntry[T] = ServiceEntry()
            entry.instance = instance
            entry.svc_type = cls_type
            entry.scope = ServiceLifetime.SINGLETON
            module_instance.services[cls_type] = entry
        else:
            raise IocException(f"Service {str(cls_type)} is already registered")

    def register_service(self, class_type: Type[T], scope: ServiceLifetime = ServiceLifetime.SINGLETON,
                         module: Type[E] = GlobalModule, register_for: Optional[Type[K]] = None, kwargs: Optional[Dict] = None) -> None:
        """
        Register a service through the class type (constructor)

        :param class_type: The service's class to register
        :param scope: The service scope (singleton or transient)
        :param module: The module to register the service into
        :param register_for: Register this service as the provided class-interface
        :param kwargs: Arguments to pass to the service constructor
        """
        if module not in self.__modules:
            module = GlobalModule

        module_instance = self.__modules[module]
        iface = class_type
        if register_for:
            iface = register_for

        if iface not in module_instance.services:
            entry: ServiceEntry[T] = ServiceEntry()
            entry.instance = None
            entry.svc_type = class_type
            entry.scope = scope
            entry.kwargs = kwargs
            module_instance.services[iface] = entry
        else:
            raise IocException(f"Service {str(class_type)} is already registered")

    def unregister(self, class_type: Type[T], module: Type[E] = GlobalModule) -> None:
        """
        Unregister a service from the given module

        :param class_type: The service to unregister
        :param module: The module to unregister the service from
        """
        if module not in self.__modules:
            module = GlobalModule

        module_instance = self.__modules[module]
        if class_type in module_instance.services:
            del module_instance.services[class_type]

    def get(self, class_type: Type[T], module: Type[E] = GlobalModule) -> Optional[T]:
        """
        Retrieve the service, or return `None` if it can't be retrieved

        :param class_type: The class name
        :param module: The module
        :return: The service, or None if not found
        """
        if module not in self.__modules:
            module = GlobalModule

        module_instance = self.__modules[module]
        if class_type in module_instance.services:
            svc = module_instance.services[class_type]
            if svc.scope == ServiceLifetime.SINGLETON:
                if svc.instance is None and svc.svc_type is not None:
                    svc.instance = svc.svc_type(**(svc.kwargs or {}))
                return svc.instance
            else:
                if svc.svc_type is not None:
                    return svc.svc_type(**(svc.kwargs or {}))
        return None

    def get_module(self, module: Type[E]):
        """
        Get a module by its class name

        :param module: The module class name
        """
        if module in self.__modules:
            return self.__modules[module]
        return None

    def register_module(self, module: Type[E]):
        """
        Register a module

        :param module: The module class name
        """
        if module not in self.__modules:
            self.__modules[module] = module()
        else:
            raise IocException(f"Module {str(module)} is already registered!")

    def unregister_module(self, module: Type[E]):
        """
        Unregister a module

        :param module: The module class name
        """
        if module in self.__modules:
            del self.__modules[module]
