"""
Per-visitor workspaces.

The frontend sends a random id in the X-Workspace header (kept in the
browser's localStorage). Every stored sentence is tagged with it and every
query is filtered by it, so visitors of a public demo never see each other's
transcripts.

Locally, requests without the header use the "default" workspace. Set
REQUIRE_WORKSPACE=1 (the Docker image does) to reject them instead.
"""
import os
import re

from fastapi import Header, HTTPException

_VALID = re.compile(r"^[A-Za-z0-9-]{8,64}$")
REQUIRE_WORKSPACE = os.getenv("REQUIRE_WORKSPACE", "0") == "1"


def workspace(x_workspace: str | None = Header(default=None)) -> str:
    if not x_workspace:
        if REQUIRE_WORKSPACE:
            raise HTTPException(400, "Missing X-Workspace header")
        return "default"
    if not _VALID.match(x_workspace):
        raise HTTPException(400, "Invalid X-Workspace header")
    return x_workspace
