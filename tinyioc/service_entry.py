from typing import TypeVar, Optional, Type, Literal, Generic, Dict

from tinyioc.types import ServiceLifetime

T = TypeVar('T')


class ServiceEntry(Generic[T]):
    """ Service model class for the IOC container """
    instance: Optional[T]
    svc_type: Optional[Type[T]]
    scope: ServiceLifetime
    kwargs: Dict
