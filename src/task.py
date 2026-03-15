from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"
    status: str = "todo"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)

    def mark_done(self):
        self.status = "done"
        self.updated_at = datetime.now().isoformat()

    def mark_todo(self):
        self.status = "todo"
        self.updated_at = datetime.now().isoformat()
