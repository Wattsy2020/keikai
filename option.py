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
    if not value:
        return Empty[T]()
    return Some(value)


def make_option(*value: T) -> Option[T]:
    if not value:
        return Empty[T]()
    return Some(*value)


def main() -> None:
    opt1: Option[int] = make_option()
    opt2 = make_option(2)
    opt3 = make_option(5)

    opts: list[Option[int]] = [opt1, opt2, opt3]
    for opt in opts:
        match opt:
            case Some(value=value):
                print(f"{opt=} {value=}")
            case Empty():
                print(f"{opt=}")

    for opt in opts:
        print(f"{opt=} {bool(opt)=}")

    def range_f(x: int) -> list[int]:
        return list(range(x))

    def sum_typed(x: list[int]) -> int:
        return sum(x)

    for opt in opts:
        result = opt | range_f | sum_typed
        print(f"piped: {result}")
        or_else_result = opt | 1000
        print(f"or_else: {or_else_result}")

    def parse_int(x: str) -> Option[int]:
        try:
            return Some(int(x))
        except ValueError:
            return Empty()

    opt4 = make_option("1")
    opt5 = make_option("hello")
    opt6: Option[str] = make_option()
    assert opt4.and_then(parse_int) == make_option(1)
    assert opt5.and_then(parse_int) == Empty[int]()
    assert opt6.and_then(parse_int) == Empty[int]()

    opt7 = from_optional(1)
    opt8: Option[int] = from_optional(None)
    print(opt7, opt7.to_optional())
    print(opt8, opt8.to_optional())


if __name__ == "__main__":
    main()
