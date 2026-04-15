from typing import runtime_checkable, Protocol


@runtime_checkable
class DbSessionFactoryInterface(Protocol):
    def get_engine(self): ...

    def get_session(self): ...