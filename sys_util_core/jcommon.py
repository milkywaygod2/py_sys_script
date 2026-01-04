from abc import ABC, abstractmethod
import threading

class ErrorSingletonBase(Exception): pass
class SingletonBase(ABC):
    _dict_instances = {}
    _dict_locks = {}

    def __new__(cls, *args, **kwargs):
        if cls not in SingletonBase._dict_instances:
            with SingletonBase._get_lock(cls):
                if cls not in SingletonBase._dict_instances:
                    SingletonBase._dict_instances[cls] = super().__new__(cls)
        return SingletonBase._dict_instances[cls]

    @staticmethod
    def _get_lock(subclass):
        # Use RLock to allow re-entrant singleton creation within the same thread
        return SingletonBase._dict_locks.setdefault(subclass, threading.RLock())

    @classmethod
    def release_instance(cls):
        with SingletonBase._get_lock(cls):
            if cls in SingletonBase._dict_instances:
                del SingletonBase._dict_instances[cls]
