"""
Decorators for module registration
"""
from .provide import ProvideInstance, ProvideSingleton, ProvideTransient
from ..container import IocContainer
from .module import IocModule
from typing import Type, TypeVar

from ..types import ServiceLifetime

E = TypeVar("E", bound=IocModule)


def module():
  """
  Declares a module to scope the injected services

  Example:

  .. code-block::

      @module()
      class MyModule(IocModule):
          pass
  """

  def inner(cls: Type[E]):
    IocContainer.get_instance().register_module(cls)

    if hasattr(cls, "provides"):
      for entry in cls.provides:
        if isinstance(entry, ProvideInstance):
          IocContainer.get_instance().register_instance(entry.entry, cls, entry.provide_for)
        elif isinstance(entry, ProvideSingleton):
          IocContainer.get_instance().register_service(entry.entry, ServiceLifetime.SINGLETON, cls,
                                                       entry.provide_for, entry.kwargs)
        elif isinstance(entry, ProvideTransient):
          IocContainer.get_instance().register_service(entry.entry, ServiceLifetime.TRANSIENT, cls,
                                                       entry.provide_for, entry.kwargs)

    return cls

  return inner
