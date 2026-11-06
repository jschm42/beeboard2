"""fix dangling foreign keys pointing to log_entries_old

Ein frueherer Tabellen-Umbau von ``log_entries`` (RENAME -> ``log_entries_old``) hat in SQLite die
Fremdschluessel der Kind-Tabellen (``inspection_details``, ``varroa_count_details``,
``varroa_treatment_details``, ``log_entry_images``) auf ``log_entries_old`` umgeschrieben. Diese Tabelle
existiert nicht mehr, daher schlaegt bei ``PRAGMA foreign_keys=ON`` jedes INSERT in diese Tabellen fehl
(z.B. Varroa-Zaehlung im Logbuch).

Die Migration korrigiert nur das Fremdschluessel-Ziel im gespeicherten Schema (SQLite-Verfahren
"writable_schema" inkl. Erhoehung von ``schema_version``). Es werden keine Tabellen geloescht oder Daten
kopiert, damit keine ON-DELETE-CASCADE-Aktionen ausgeloest werden. Auf anderen Datenbanken und auf
bereits korrekten Schemata ist die Migration ein No-op.

Revision ID: b3c4d5e6f7a8
Revises: a7b8c9d0e1f2
Create Date: 2026-11-06 10:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STALE_TARGET = "log_entries_old"
CORRECT_TARGET = "log_entries"


def _tables_with_stale_fk(conn) -> list[str]:
    table_names = [
        row[0]
        for row in conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type = 'table'")
    ]
    affected = []
    for table in table_names:
        fks = conn.exec_driver_sql(f'PRAGMA foreign_key_list("{table}")').fetchall()
        # Spalte 2 von foreign_key_list ist die referenzierte Tabelle
        if any(fk[2] == STALE_TARGET for fk in fks):
            affected.append(table)
    return affected


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name != "sqlite":
        return

    inspector = sa.inspect(conn)
    existing = set(inspector.get_table_names())
    if CORRECT_TARGET not in existing or STALE_TARGET in existing:
        return

    affected = _tables_with_stale_fk(conn)
    if not affected:
        return

    schema_version = conn.exec_driver_sql("PRAGMA schema_version").scalar()
    conn.exec_driver_sql("PRAGMA writable_schema = ON")
    for table in affected:
        conn.execute(
            sa.text(
                "UPDATE sqlite_master SET sql = replace(replace(sql, :quoted_old, :new), :bare_old, :new) "
                "WHERE type = 'table' AND name = :name"
            ),
            {
                "quoted_old": f'REFERENCES "{STALE_TARGET}"',
                "bare_old": f"REFERENCES {STALE_TARGET}",
                "new": f"REFERENCES {CORRECT_TARGET}",
                "name": table,
            },
        )
    conn.exec_driver_sql(f"PRAGMA schema_version = {int(schema_version) + 1}")
    conn.exec_driver_sql("PRAGMA writable_schema = OFF")

    integrity = conn.exec_driver_sql("PRAGMA integrity_check").scalar()
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check nach FK-Reparatur fehlgeschlagen: {integrity}")


def downgrade() -> None:
    # Bewusst kein Rueckweg: der vorherige Zustand war ein defektes Schema.
    pass
