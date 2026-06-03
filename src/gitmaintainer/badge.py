from __future__ import annotations

from urllib.parse import quote

COLORS = {
    "Active": "brightgreen",
    "Slow": "yellow",
    "Risky": "orange",
    "Abandoned": "red",
}


def badge_markdown(owner: str, repo: str, status: str) -> str:
    label = quote("maintenance")
    message = quote(status.lower())
    color = COLORS.get(status, "lightgrey")
    image = f"https://img.shields.io/badge/{label}-{message}-{color}"
    target = f"https://github.com/{owner}/{repo}"
    return f"[![Maintenance status]({image})]({target})"
