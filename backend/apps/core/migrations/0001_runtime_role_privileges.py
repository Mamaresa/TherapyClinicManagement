"""Baseline privileges for the restricted runtime role (issue N1).

Runs as the owner role. Tables created by the owner from now on give the
runtime role SELECT, INSERT and UPDATE only: never DELETE, TRUNCATE,
REFERENCES or TRIGGER, and the runtime role owns nothing, so it cannot ALTER,
DROP or disable triggers. Tables that need more restriction (append-only,
column-limited updates) revoke further in their own migrations.
"""

from django.db import migrations

from apps.core.db import runtime_role_sql

GRANTS = """
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO {role};
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {role};
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {role};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO {role};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO {role};
-- Logout and session rotation delete session rows.
GRANT DELETE ON django_session TO {role};
"""

UNDO_GRANTS = """
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM {role};
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM {role};
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {role};
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM {role};
REVOKE USAGE ON SCHEMA public FROM {role};
"""

# One shared trigger function for append-only tables. It is owned by the
# owner role, so the runtime role cannot replace or drop it.
FORBID_CHANGE = """
CREATE FUNCTION forbid_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% on % is not allowed: the table is append-only', TG_OP, TG_TABLE_NAME
        USING ERRCODE = 'insufficient_privilege';
END;
$$;
"""


class Migration(migrations.Migration):
    dependencies = [("sessions", "0001_initial")]

    operations = [
        runtime_role_sql(GRANTS, UNDO_GRANTS),
        migrations.RunSQL(FORBID_CHANGE, "DROP FUNCTION forbid_change()"),
    ]
