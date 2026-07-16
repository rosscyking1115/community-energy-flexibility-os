"""Shared HTTP helper for the data-source clients - one place for the GET
boilerplate (headers, timeout, JSON decode)."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

USER_AGENT = "community-energy-flex/0.2 (+https://github.com/rosscyking1115/community-energy-flex)"


def get_json(url: str, timeout: int = 20) -> dict:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https hosts
        return json.loads(resp.read().decode("utf-8"))
