import importlib.util
import os

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

MIGRATION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "alembic", "versions", "b3c4d5e6f7a8_fix_dangling_log_entries_old_fks.py"
)


def _load_migration():
    spec = importlib.util.spec_from_file_location("fix_log_entries_fk", MIGRATION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _foreign_key_targets(conn, table: str) -> set[str]:
    return {row[2] for row in conn.exec_driver_sql(f'PRAGMA foreign_key_list("{table}")')}


def test_migration_repoints_dangling_log_entries_old_fks(tmp_path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'broken.db'}")
    with engine.begin() as conn:
        # Build the broken legacy state; with FK checks on, the insert below fails exactly like the app did.
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.exec_driver_sql("CREATE TABLE log_entries (id VARCHAR(36) PRIMARY KEY)")
        conn.exec_driver_sql(
            "CREATE TABLE varroa_count_details (id VARCHAR(36) PRIMARY KEY, log_entry_id VARCHAR(36), "
            'FOREIGN KEY(log_entry_id) REFERENCES "log_entries_old" (id) ON DELETE CASCADE)'
        )
        conn.exec_driver_sql(
            "CREATE TABLE inspection_details (id VARCHAR(36) PRIMARY KEY, log_entry_id VARCHAR(36), "
            'FOREIGN KEY(log_entry_id) REFERENCES "log_entries_old" (id) ON DELETE CASCADE)'
        )
        conn.exec_driver_sql("INSERT INTO log_entries VALUES ('e1')")
        conn.exec_driver_sql("INSERT INTO inspection_details VALUES ('i1', 'e1')")

    migration = _load_migration()
    with engine.begin() as conn:
        with Operations.context(MigrationContext.configure(conn)):
            migration.upgrade()

    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        assert _foreign_key_targets(conn, "varroa_count_details") == {"log_entries"}
        assert _foreign_key_targets(conn, "inspection_details") == {"log_entries"}
        conn.exec_driver_sql("INSERT INTO varroa_count_details VALUES ('v1', 'e1')")
        assert conn.exec_driver_sql("SELECT count(*) FROM inspection_details").scalar() == 1
        assert conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall() == []


def test_migration_is_noop_on_healthy_schema(tmp_path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'healthy.db'}")
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE log_entries (id VARCHAR(36) PRIMARY KEY)")
        conn.exec_driver_sql(
            "CREATE TABLE varroa_count_details (id VARCHAR(36) PRIMARY KEY, log_entry_id VARCHAR(36), "
            "FOREIGN KEY(log_entry_id) REFERENCES log_entries (id))"
        )
        version_before = conn.exec_driver_sql("PRAGMA schema_version").scalar()

    migration = _load_migration()
    with engine.begin() as conn:
        with Operations.context(MigrationContext.configure(conn)):
            migration.upgrade()
        assert conn.exec_driver_sql("PRAGMA schema_version").scalar() == version_before
