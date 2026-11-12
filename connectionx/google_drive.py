"""Google Drive seat - the file home for the service, PLAN ONLY.

ConnectionX keeps its files in named Drive folders: code, configs,
logs, exports, backups, Flow storyboards (media), reports, and the
archive. This module keeps the local registry for that plan: every
file gets a SHA-256 fingerprint, and one name maps to one hash - a
second, different file with the same name is HELD as a conflict,
never overwritten (the CloudBrain rule).

Nothing is uploaded: live connections are 0, and reading or writing
a real Drive is HOLD gate ``google_drive_access`` until the owner
connects and approves it himself.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

DRIVE_FOLDERS = ["code", "configs", "data", "docs", "media",
                 "backups", "logs", "exports", "reports", "archive"]

_FOLDER_BY_EXT = {
    ".py": "code", ".yml": "configs", ".yaml": "configs",
    ".json": "data", ".md": "docs", ".png": "media", ".jpg": "media",
    ".log": "logs", ".csv": "exports", ".zip": "backups",
}


def folder_for(filename: str) -> str:
    lower = filename.lower()
    for ext, folder in _FOLDER_BY_EXT.items():
        if lower.endswith(ext):
            return folder
    if "report" in lower:
        return "reports"
    return "archive"


@dataclass
class DriveRegistry:
    """Local registry for the Drive plan. One name, one hash."""

    files: dict[str, dict] = field(default_factory=dict)
    conflicts: list[dict] = field(default_factory=list)

    def register(self, filename: str, data: bytes) -> dict:
        digest = hashlib.sha256(data).hexdigest()
        existing = self.files.get(filename)
        if existing and existing["sha256"] != digest:
            conflict = {"name": filename, "kept_sha256": existing["sha256"],
                        "rejected_sha256": digest, "status": "HOLD-CONFLICT"}
            self.conflicts.append(conflict)
            return conflict
        record = {"name": filename, "folder": folder_for(filename),
                  "sha256": digest, "bytes": len(data),
                  "status": "registered-local", "uploaded": False}
        self.files[filename] = record
        return record

    def summary(self) -> dict:
        return {
            "platform": "Google Drive",
            "folders": DRIVE_FOLDERS,
            "registered": len(self.files),
            "conflicts_held": len(self.conflicts),
            "uploaded": 0,
            "live_connections": 0,
            "gate": "google_drive_access = HOLD until the owner connects Drive",
        }
