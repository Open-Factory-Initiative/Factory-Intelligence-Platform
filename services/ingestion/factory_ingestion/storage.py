from __future__ import annotations

import json
from pathlib import Path

from factory_events import EventEnvelope, validate_event


class JsonlEventStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: EventEnvelope) -> None:
        with self.path.open("a", encoding="utf-8") as output:
            output.write(json.dumps(event.model_dump(mode="json"), sort_keys=True))
            output.write("\n")

    def list_events(self) -> list[EventEnvelope]:
        if not self.path.exists():
            return []
        events: list[EventEnvelope] = []
        with self.path.open(encoding="utf-8") as input_file:
            for line in input_file:
                if line.strip():
                    events.append(validate_event(json.loads(line)))
        return events

    def get_event(self, event_id: str) -> EventEnvelope | None:
        return next((event for event in self.list_events() if event.event_id == event_id), None)


class PostgresEventStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def append(self, event: EventEnvelope) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into factory_events (
                        event_id,
                        event_type,
                        schema_version,
                        event_timestamp,
                        trace_id,
                        simulated,
                        event_body
                    )
                    values (%s, %s, %s, %s, %s, %s, %s)
                    on conflict (event_id) do nothing
                    """,
                    (
                        event.event_id,
                        event.event_type,
                        event.schema_version,
                        event.timestamp,
                        event.metadata.trace_id,
                        event.metadata.simulated,
                        json.dumps(event.model_dump(mode="json")),
                    ),
                )
