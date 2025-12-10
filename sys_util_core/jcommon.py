from abc import ABC, abstractmethod
from threading import Lock

class SingletonBase(ABC):
    _dict_instances = {}
    _dict_locks = {}

    @abstractmethod
    def __new__(cls, *args, **kwargs):
        if cls not in SingletonBase._dict_instances:
            with SingletonBase._get_lock(cls):
                if cls not in SingletonBase._dict_instances:
                    SingletonBase._dict_instances[cls] = super().__new__(cls)
        return SingletonBase._dict_instances[cls]

    @staticmethod
    def _get_lock(subclass):
        if subclass not in SingletonBase._dict_locks:
            SingletonBase._dict_locks[subclass] = Lock()
        return SingletonBase._dict_locks[subclass]

    @classmethod
    def release_instance(cls):
        with SingletonBase._get_lock(cls):
            if cls in SingletonBase._dict_instances:
                del SingletonBase._dict_instances[cls]