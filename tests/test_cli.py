import pytest

from gitmaintainer.github import parse_repo


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("pallets/flask", ("pallets", "flask")),
        ("github.com/pallets/flask", ("pallets", "flask")),
        ("https://github.com/pallets/flask.git", ("pallets", "flask")),
    ],
)
def test_parse_repo(value: str, expected: tuple[str, str]) -> None:
    assert parse_repo(value) == expected


def test_parse_repo_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        parse_repo("not-a-repo")
