from typing import Union, Type, TypeVar, Dict, Optional

T = TypeVar("T")
E = TypeVar("E")


class Provide:
    """ Base class for service provision in modules """
    entry: Union[T, Type[T]]
    provide_for: Optional[Type[E]]
    kwargs: Optional[Dict]


class ProvideInstance(Provide):
    """ Class for providing instances in modules """
    def __init__(self, entry: T, provide_for: Optional[Type[E]] = None):
        """
        :param entry: The instance to register
        :param provide_for: The interface class to register this instance as
        """
        self.entry = entry
        self.provide_for = provide_for


class ProvideSingleton(Provide):
    """ Class for providing singletons in modules """
    def __init__(self, entry: Type[T], provide_for: Optional[Type[E]] = None, **kwargs):
        """
        :param entry: The class to register
        :param provide_for: The interface class to register this instance as
        :param kwargs: Arguments for the class constructor
        """
        self.entry = entry
        self.provide_for = provide_for
        self.kwargs = kwargs


class ProvideTransient(Provide):
    """ Class for providing transient services in modules """
    def __init__(self, entry: Type[T], provide_for: Optional[Type[E]] = None, **kwargs):
        """
        :param entry: The class to register
        :param provide_for: The interface class to register this instance as
        :param kwargs: Arguments for the class constructor
        """
        self.entry = entry
        self.provide_for = provide_for
        self.kwargs = kwargs
