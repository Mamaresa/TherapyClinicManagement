"""Database-level protections for accounts tables (issues N1, N3).

- Composite FK: a grant can only point at a membership of the same tenant.
- Column-limited UPDATE for the runtime role: membership history (user,
  tenant, joined_at) and grant history (membership, code, granted_at) cannot
  be rewritten; only roles/ended_at and revoked_at can change.
"""

from django.db import migrations

from apps.core.db import composite_fk, runtime_role_sql

PRIVILEGES = """
REVOKE UPDATE ON tenant_membership FROM {role};
GRANT UPDATE (roles, ended_at) ON tenant_membership TO {role};
REVOKE UPDATE ON membership_grant FROM {role};
GRANT UPDATE (revoked_at) ON membership_grant TO {role};
"""

UNDO_PRIVILEGES = """
GRANT UPDATE ON tenant_membership TO {role};
GRANT UPDATE ON membership_grant TO {role};
"""


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("core", "0001_runtime_role_privileges"),
    ]

    operations = [
        composite_fk("membership_grant", "fk_mg_membership_tenant", ["membership_id", "tenant_id"],
                     "tenant_membership", ["id", "tenant_id"]),
        runtime_role_sql(PRIVILEGES, UNDO_PRIVILEGES),
    ]
