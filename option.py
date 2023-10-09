from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeAlias, TypeVar, overload

T = TypeVar("T")
T1 = TypeVar("T1")
Option: TypeAlias = "Some[T] | Empty[T]"


class Optional(ABC, Generic[T]):
    def __init__(self, *value: T) -> None:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        ...

    @abstractmethod
    def unwrap(self) -> T:
        ...

    @abstractmethod
    def or_else(self, other: T) -> T:
        ...

    @abstractmethod
    def transform(self, f: Callable[[T], T1]) -> Option[T1]:
        ...

    @abstractmethod
    def and_then(self, f: Callable[[T], Option[T1]]) -> Option[T1]:
        ...

    @overload
    def __or__(self, other: Callable[[T], T1]) -> Option[T1]:  # type: ignore[misc]
        ...

    @overload
    def __or__(self, other: T) -> T:
        ...

    def __or__(self, other: T | Callable[[T], T1]) -> T | Option[T1]:  # type: ignore[misc]
        if callable(other):
            return self.transform(other)
        return self.or_else(other)

    @abstractmethod
    def to_optional(self) -> T | None:
        ...


class Some(Optional[T]):
    def __init__(self, *value: T) -> None:
        try:
            first, *remaining = value
        except ValueError:
            raise ValueError("A value must be provided to a Some object")
        if remaining:
            raise ValueError("Only one value should be provided to a Some object")
        self.value = first

    def __repr__(self) -> str:
        return f"Some({self.value})"

    def __bool__(self) -> bool:
        return True

    def __eq__(self, other: Any) -> bool:
        match other:
            case Some():
                return self.value == other.value
            case _:
                return False

    def unwrap(self) -> T:
        return self.value

    def or_else(self, other: T) -> T:
        return self.value

    def transform(self, f: Callable[[T], T1]) -> Option[T1]:
        return Some(f(self.value))

    def and_then(self, f: Callable[[T], Option[T1]]) -> Option[T1]:
        return f(self.value)

    def to_optional(self) -> T | None:
        return self.value


class Empty(Optional[T]):
    def __init__(self, *value: T) -> None:
        if value:
            raise ValueError(f"Cannot assign the value {value} to an Empty object")

    def __repr__(self) -> str:
        return "Empty"

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Empty)

    def unwrap(self) -> T:
        raise ValueError("Empty object has no value to unwrap")

    def or_else(self, other: T) -> T:
        return other

    def transform(self, f: Callable[[T], T1]) -> Option[T1]:
        return Empty[T1]()

    def and_then(self, f: Callable[[T], Option[T1]]) -> Option[T1]:
        return Empty[T1]()

    def to_optional(self) -> T | None:
        return None


def from_optional(value: T | None) -> Option[T]:
    if value is None:
        return Empty[T]()
    return Some(value)


def make_option(*value: T) -> Option[T]:
    if not value:
        return Empty[T]()
    return Some(*value)
