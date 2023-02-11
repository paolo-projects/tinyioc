"""
Helper functions to register and retrieve services procedurally
"""

from .container import IocContainer
from typing import Type, TypeVar, Optional
from .module.module import IocModule, GlobalModule
from .types import ServiceLifetime

T = TypeVar("T")
K = TypeVar("K")
E = TypeVar("E", bound=IocModule)


def register_instance(instance: T, module: Type[E] = GlobalModule, register_for: Optional[Type[K]] = None):
    """
    Register the instance of a service

    :param instance: The instance of the service
    :param module: The module to register this instance into
    :param register_for: The class-interface to register this instance as
    """
    IocContainer.get_instance().register_instance(instance, module, register_for=register_for)


def register_singleton(cls: Type[T], module: Type[E] = GlobalModule, register_for: Optional[Type[K]] = None, **kwargs):
    """
    Register a class with singleton scope (one instance shared across the module)

    :param cls: The class to register
    :param module: The module to register the service into
    :param register_for: The class-interface to register this service as
    """
    IocContainer.get_instance().register_service(cls, ServiceLifetime.SINGLETON, module, register_for, kwargs)


def register_transient(cls: Type[T], module: Type[E] = GlobalModule, register_for: Optional[Type[K]] = None, **kwargs):
    """
    Register a class with transient scope (new instance every time the service is injected)

    :param cls: The class to register
    :param module: The module to register the service into
    :param register_for: The class-interface to register this service as
    """
    IocContainer.get_instance().register_service(cls, ServiceLifetime.TRANSIENT, module, register_for, kwargs)


def unregister_service(cls: Type[T], module: Type[E] = GlobalModule):
    """
    Unregister a service

    :param cls: The service class
    :param module: The module from which to unregister
    """
    IocContainer.get_instance().unregister(cls, module)


def unregister_module(module: Type[E]):
    """
    Unregister a module

    :param module: The module to unregister
    """
    IocContainer.get_instance().unregister_module(module)


def get_service(cls: Type[T], module: Type[E] = GlobalModule) -> Optional[T]:
    """
    Retrieve a service from the container

    :param cls: The service class
    :param module: The module to retrieve the service from
    :return: The service, or `None` if it couldn't be retrieved
    """
    return IocContainer.get_instance().get(cls, module)
