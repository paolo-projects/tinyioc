from enum import Enum


class ServiceLifetime(Enum):
    """
    The service lifetime. Can be singleton (one instance shared through the whole app)
    or transient (new instance every time it is injected)
    """
    SINGLETON = 0
    """Singleton scope: one instance shared through the whole app"""
    TRANSIENT = 1
    """Transient scope: new instance every time it is injected"""
