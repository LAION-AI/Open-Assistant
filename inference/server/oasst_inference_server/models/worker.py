import datetime
import enum
from uuid import uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from oasst_shared.schemas import inference
from sqlmodel import Field, Relationship, SQLModel


class WorkerEventType(str, enum.Enum):
    connect = "connect"


class DbWorkerComplianceCheck(SQLModel, table=True):
    __tablename__ = "worker_compliance_check"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    worker_id: str = Field(foreign_key="worker.id", index=True)
    worker: "DbWorker" = Relationship(back_populates="compliance_checks")
    compare_worker_id: str = Field(foreign_key="worker.id", index=True)

    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    end_time: datetime.datetime | None = Field(None, nullable=True)
    responded: bool = Field(default=False, nullable=False)
    error: str | None = Field(None, nullable=True)
    passed: bool = Field(default=False, nullable=False)


class DbWorkerEvent(SQLModel, table=True):
    __tablename__ = "worker_event"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    worker_id: str = Field(foreign_key="worker.id", index=True)
    worker: "DbWorker" = Relationship(back_populates="events")
    time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    event_type: WorkerEventType
    worker_config: inference.WorkerConfig | None = Field(None, sa_column=sa.Column(pg.JSONB))


class DbWorker(SQLModel, table=True):
    __tablename__ = "worker"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    api_key: str = Field(default_factory=lambda: str(uuid4()), index=True)
    name: str

    compliance_checks: list[DbWorkerComplianceCheck] = Relationship(back_populates="worker")
    in_compliance_check: bool = Field(default=False, sa_column=sa.Column(sa.Boolean, server_default=sa.text("false")))
    next_compliance_check: datetime.datetime | None = Field(None)
    events: list[DbWorkerEvent] = Relationship(back_populates="worker")
