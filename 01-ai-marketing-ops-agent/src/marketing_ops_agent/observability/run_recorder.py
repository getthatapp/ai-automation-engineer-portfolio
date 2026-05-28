"""JSONL-backed local workflow run recorder."""

import json
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from marketing_ops_agent.observability.errors import MalformedRunRecordLineError
from marketing_ops_agent.observability.models import WorkflowRunRecord

DEFAULT_RUN_RECORDS_PATH = Path("run-history") / "workflow-runs.jsonl"


class LocalRunRecorder:
    """Append and read typed workflow run records from a local JSONL file."""

    def __init__(self, path: Path | str = DEFAULT_RUN_RECORDS_PATH) -> None:
        self.path = Path(path)

    def append(self, record: WorkflowRunRecord) -> None:
        """Append one run record, creating the storage directory if needed."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{record.model_dump_json()}\n")

    def read_recent(self, limit: int = 20) -> list[WorkflowRunRecord]:
        """Read the most recent records in chronological order."""

        if limit < 0:
            raise ValueError("limit must be greater than or equal to 0")
        if limit == 0 or not self.path.exists():
            return []

        records = self._read_all()
        return records[-limit:]

    def get(self, run_id: str) -> WorkflowRunRecord | None:
        """Return the most recent record with the requested run ID, if present."""

        normalized_run_id = run_id.strip()
        if not normalized_run_id or not self.path.exists():
            return None

        for record in reversed(self._read_all()):
            if record.run_id == normalized_run_id:
                return record
        return None

    def _read_all(self) -> list[WorkflowRunRecord]:
        records: list[WorkflowRunRecord] = []
        with self.path.open(encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                stripped = line.strip()
                if not stripped:
                    raise MalformedRunRecordLineError(
                        path=self.path,
                        line_number=line_number,
                        reason="empty JSONL line",
                    )
                records.append(self._parse_line(stripped, line_number))
        return records

    def _parse_line(self, line: str, line_number: int) -> WorkflowRunRecord:
        try:
            decoded: Any = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MalformedRunRecordLineError(
                path=self.path,
                line_number=line_number,
                reason="invalid JSON",
            ) from exc

        if not isinstance(decoded, dict):
            raise MalformedRunRecordLineError(
                path=self.path,
                line_number=line_number,
                reason="JSON value is not an object",
            )

        try:
            return WorkflowRunRecord.model_validate(cast(dict[str, object], decoded))
        except ValidationError as exc:
            raise MalformedRunRecordLineError(
                path=self.path,
                line_number=line_number,
                reason="record schema validation failed",
            ) from exc
