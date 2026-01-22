from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ColumnModel:
    name: str
    sql_type: str
    nullable: bool = True
    is_primary_key: bool = False
    is_auto_increment: bool = False


@dataclass
class TableModel:
    name: str
    columns: List[ColumnModel] = field(default_factory=list)
    rows: List[dict] = field(default_factory=list)

    @property
    def primary_keys(self) -> list[ColumnModel]:
        return [col for col in self.columns if col.is_primary_key]


@dataclass
class DatabaseProject:
    database_name: str
    tables: List[TableModel] = field(default_factory=list)
    dbms: str = "SQL Server"  # Matches UI values: "SQL Server", "MySQL", "PostgreSQL"
