from abc import ABC, abstractmethod
from threading import Lock

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
        return SingletonBase._dict_locks.setdefault(subclass, Lock())

    @classmethod
    def release_instance(cls):
        with SingletonBase._get_lock(cls):
            if cls in SingletonBase._dict_instances:
                del SingletonBase._dict_instances[cls]