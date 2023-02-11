"""
Decorators to inject and register services
"""

import inspect
from typing import Callable, TypeVar, Type, Optional
from .container import IocContainer
from .module.module import GlobalModule, IocModule, FromModule
from inspect import signature, Parameter

from .types import ServiceLifetime

T = TypeVar("T")
K = TypeVar("K")
E = TypeVar("E", bound=IocModule)


def inject(module: Type[E] = GlobalModule):
  """
  Inject one or more services from the IOC container
  into the function. If the function named arguments
  already include the service name, the argument is
  NOT overwritten, instead forwarding the original one.

  Example:

  .. code-block::

      @inject()
      def endpoint(database_service: DbService):
          user = database_service.getUser(...)
          ...

  This behavior is optimal for tests, where you call the
  function with your mocked object. e.g.

  .. code-block::

      @inject()
      def my_fun(api_service: ApiService):
          ...

      # -----------------------
      # Test:
      api_mock = ApiServiceMock()
      my_fun(api_service=api_mock)
      ...

  :param module: The module to retrieve the service from (defaults to the global module)
  """

  def inner(fn: Callable):
    # Get the function signature (declared parameters)
    sig = signature(fn)

    def wrapper(*args, **kwargs):
      inj_kwargs = {}

      for param in sig.parameters:
        param_def = sig.parameters[param].default
        cls_type = sig.parameters[param].annotation
        # If the function parameter is a named service in the container,
        # and it has not been already provided to the function, inject it
        if cls_type is not Parameter.empty and param not in kwargs:
          param_module = module
          param_cls = cls_type

          if isinstance(param_def, FromModule):
            param_module = param_def.module

          svc_instance = IocContainer.get_instance().get(param_cls, param_module)
          if svc_instance is not None:
            inj_kwargs[param] = svc_instance

      # Merge the original parameters with the injected services
      kwargs.update(inj_kwargs)
      return fn(*args, **kwargs)

    return wrapper

  return inner


def inject_getter(module: Type[E] = GlobalModule):
  """
  Transform a class member function (or any other kind of function) into
  a service getter, by its return type

  Example:

  .. code-block::

      class MyClass:
          @inject_getter()
          def get_api_service() -> ApiService:
              pass

  :param module: The module to retrieve the service from
  """

  def inner(fn: Callable[[], T]) -> Callable[[], T]:
    def wrapper(*args, **kwargs):
      svc = IocContainer.get_instance().get(ret_type, module)
      return svc

    sig = inspect.signature(fn)
    ret_type = sig.return_annotation

    if ret_type is not Parameter.empty:
      return wrapper
    else:
      return fn

  return inner


def injectable(scope: ServiceLifetime = ServiceLifetime.SINGLETON, module: Type[E] = GlobalModule,
               register_for: Optional[Type[K]] = None, **kwargs):
  """
  Registers the class into the IOC container

  Example:

  .. code-block::

      @injectable("singleton")
      class MailService:
          ...

  :param scope: The scope of this service (singleton, transient)
  :param module: The module to register this service into
  :param register_for: Register this instance for the provided class-interface
  :param kwargs: Params to call the class constructor with
  """

  def inner(cls: Type[T]) -> Type[T]:
    IocContainer.get_instance().register_service(cls, scope, module, register_for, kwargs)
    return cls

  return inner
