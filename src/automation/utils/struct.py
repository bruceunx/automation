from dataclasses import dataclass, field

from utils.constant import EmpployeeType, Platform, PublishType


@dataclass
class Position:
    id: int
    title: str
    permission: int


@dataclass
class Employee:
    id: int
    name: str
    phone_number: int
    status: EmpployeeType
    positions: list[Position] = field(default_factory=list)


@dataclass
class Record:
    id: int
    timestamp: int
    title: str
    status: int
    username: str
    platform: Platform
    icon_raw: str
    record_type: PublishType
