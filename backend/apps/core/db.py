"""Small helpers for hand-written SQL in migrations."""

from django.conf import settings
from django.db import migrations


def runtime_role_sql(forward, backward=""):
    """Run SQL that mentions the runtime role, written as {role}.

    The role name comes from settings.DB_RUNTIME_ROLE so the same migration
    works in every environment.
    """

    def _run(sql):
        def apply(apps, schema_editor):
            if sql:
                role = schema_editor.connection.ops.quote_name(settings.DB_RUNTIME_ROLE)
                schema_editor.execute(sql.format(role=role))

        return apply

    return migrations.RunPython(_run(forward), _run(backward))


def composite_fk(table, name, columns, ref_table, ref_columns):
    """FOREIGN KEY (columns) REFERENCES ref_table (ref_columns).

    Django cannot declare multi-column foreign keys, so tenant-consistency
    keys are added with SQL.
    """
    cols = ", ".join(columns)
    refs = ", ".join(ref_columns)
    return migrations.RunSQL(
        f"ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({cols}) "
        f"REFERENCES {ref_table} ({refs}) ON DELETE RESTRICT ON UPDATE RESTRICT",
        f"ALTER TABLE {table} DROP CONSTRAINT {name}",
    )
