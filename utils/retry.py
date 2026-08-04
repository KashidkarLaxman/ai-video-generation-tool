from typing import Callable, TypeVar


T = TypeVar("T")


def retry(func: Callable[[], T], attempts: int = 2) -> T:
    last_error = None
    for _ in range(attempts):
        try:
            return func()
        except Exception as exc:
            last_error = exc
    raise last_error
