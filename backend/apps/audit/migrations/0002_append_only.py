"""audit_event is append-only (issue N1).

Two independent layers:
1. Privileges: the runtime role may only SELECT and INSERT.
2. Triggers (ENABLE ALWAYS) reject UPDATE, DELETE and TRUNCATE for every
   role except the table owner, who could disable them. The runtime role is
   not the owner, so it can neither run those statements nor disable the
   triggers.
"""

from django.db import migrations

from apps.core.db import runtime_role_sql

PRIVILEGES = "REVOKE UPDATE, DELETE, TRUNCATE ON audit_event FROM {role};"
UNDO_PRIVILEGES = "GRANT UPDATE ON audit_event TO {role};"

TRIGGERS = """
CREATE TRIGGER audit_event_append_only
    BEFORE UPDATE OR DELETE ON audit_event
    FOR EACH ROW EXECUTE FUNCTION forbid_change();
CREATE TRIGGER audit_event_no_truncate
    BEFORE TRUNCATE ON audit_event
    FOR EACH STATEMENT EXECUTE FUNCTION forbid_change();
ALTER TABLE audit_event ENABLE ALWAYS TRIGGER audit_event_append_only;
ALTER TABLE audit_event ENABLE ALWAYS TRIGGER audit_event_no_truncate;
"""

UNDO_TRIGGERS = """
DROP TRIGGER audit_event_no_truncate ON audit_event;
DROP TRIGGER audit_event_append_only ON audit_event;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
        ("core", "0001_runtime_role_privileges"),
    ]

    operations = [
        runtime_role_sql(PRIVILEGES, UNDO_PRIVILEGES),
        migrations.RunSQL(TRIGGERS, UNDO_TRIGGERS),
    ]
