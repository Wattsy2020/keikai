from __future__ import annotations

import typing

import pytest
from typing_extensions import assert_type

from option import Empty, Optional, Some, from_optional, make_option


@pytest.fixture()
def opt_list() -> list[Optional[int]]:
    return [make_option(), make_option(2)]


def test_make_option() -> None:
    empty: Optional[int] = make_option()
    assert isinstance(empty, Empty)
    some = make_option(1)
    assert_type(some, "Optional[int]")
    assert isinstance(some, Some)


def test_some_none() -> None:
    some_none = make_option(None)
    assert_type(some_none, "Optional[None]")
    assert some_none.unwrap() == None


def test_equality() -> None:
    assert make_option(1) == make_option(1)
    assert make_option(1) != 1
    assert make_option(1) != make_option()
    assert make_option() == make_option()
    assert make_option() != None


def test_optional_conversion() -> None:
    empty: Optional[int] = from_optional(None)
    assert_type(empty, "Optional[int]")
    assert empty == Empty()
    some = from_optional(1)
    assert_type(some, "Optional[int]")
    assert some == Some(1)

    empty_opt = empty.to_optional()
    assert_type(empty_opt, "int | None")
    assert_type(empty_opt, "typing.Optional[int]")
    assert empty_opt is None

    some_opt = some.to_optional()
    assert_type(some_opt, "int | None")
    assert_type(some_opt, "typing.Optional[int]")
    assert some_opt == 1


def test_match_statement(opt_list: list[Optional[int]]) -> None:
    for opt in opt_list:
        match opt:
            case Some(value=value):
                assert value == 2
                assert opt.value == 2
                assert str(opt) == "Some(2)"
                assert bool(opt) is True
            case Empty():
                assert not hasattr(opt, "value")
                assert str(opt) == "Empty"
                assert bool(opt) is False
    return


def test_unwrap() -> None:
    empty: Optional[int] = make_option()
    with pytest.raises(ValueError):
        empty.unwrap()
    assert make_option(2).unwrap() == 2


def test_or_else() -> None:
    empty: Optional[int] = make_option()
    assert empty.or_else(10) == 10
    empty_or = empty | 10
    assert_type(empty_or, int)
    assert empty_or == 10

    some = make_option(2)
    assert some.or_else(10) == 2
    some_or = some | 10
    assert_type(some_or, int)


def test_pipelining() -> None:
    def range_f(x: int) -> list[int]:
        return list(range(x))

    def sum_typed(x: list[int]) -> int:
        return sum(x)

    empty: Optional[int] = make_option()
    empty_piped = empty | range_f | sum_typed | str
    assert_type(empty_piped, "Optional[str]")
    assert empty_piped == Empty()

    some = make_option(5)
    some_piped = some | range_f | sum_typed | str
    assert_type(some_piped, "Optional[str]")
    assert some_piped == Some("10")


def test_and_then() -> None:
    def parse_int(x: str) -> Optional[int]:
        try:
            return Some(int(x))
        except ValueError:
            return Empty()

    empty: Optional[str] = make_option()
    empty_result = empty.and_then(parse_int)
    assert_type(empty_result, "Optional[int]")
    assert empty_result == Empty()

    some1 = make_option("1")
    some1_result = some1.and_then(parse_int)
    assert_type(some1_result, "Optional[int]")
    assert some1_result == Some(1)

    some2 = make_option("hello")
    some2_result = some2.and_then(parse_int)
    assert_type(some2_result, "Optional[int]")
    assert some2_result == Empty()
