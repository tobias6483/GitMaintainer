import pytest

from urllib.error import HTTPError

from gitmaintainer.github import _http_error_message, parse_repo


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("pallets/flask", ("pallets", "flask")),
        ("github.com/pallets/flask", ("pallets", "flask")),
        ("https://github.com/pallets/flask.git", ("pallets", "flask")),
        ("git@github.com:pallets/flask.git", ("pallets", "flask")),
    ],
)
def test_parse_repo(value: str, expected: tuple[str, str]) -> None:
    assert parse_repo(value) == expected


def test_parse_repo_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        parse_repo("not-a-repo")


def test_rate_limit_error_is_actionable() -> None:
    error = HTTPError(
        url="https://api.github.com/repos/owner/repo",
        code=403,
        msg="Forbidden",
        hdrs=None,
        fp=_Body(b'{"message":"API rate limit exceeded for 127.0.0.1"}'),
    )

    message = _http_error_message(error, error.url)

    assert "rate limit exceeded" in message
    assert "GITHUB_TOKEN" in message


class _Body:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def read(self) -> bytes:
        return self.body

    def close(self) -> None:
        return None
