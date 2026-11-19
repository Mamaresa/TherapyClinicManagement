"""Database-level protections for care-team tables (issues N1, N3, N4).

- Composite FKs: patient, therapist and supervisor must all belong to the
  same tenant as the assignment / supervision row.
- Column-limited UPDATE for the runtime role: an assignment or supervision
  can be ended (ended_at) but never rewritten to another patient, therapist
  or supervisor.
"""

from django.db import migrations

from apps.core.db import composite_fk, runtime_role_sql

PRIVILEGES = """
REVOKE UPDATE ON clinical_assignment FROM {role};
GRANT UPDATE (ended_at) ON clinical_assignment TO {role};
REVOKE UPDATE ON clinical_supervision FROM {role};
GRANT UPDATE (ended_at) ON clinical_supervision TO {role};
"""

UNDO_PRIVILEGES = """
GRANT UPDATE ON clinical_assignment TO {role};
GRANT UPDATE ON clinical_supervision TO {role};
"""


class Migration(migrations.Migration):
    dependencies = [
        ("patients", "0001_initial"),
        ("accounts", "0002_db_security"),
    ]

    operations = [
        composite_fk("clinical_assignment", "fk_ca_patient_tenant", ["patient_id", "tenant_id"],
                     "patient", ["id", "tenant_id"]),
        composite_fk("clinical_assignment", "fk_ca_therapist_tenant", ["therapist_membership_id", "tenant_id"],
                     "tenant_membership", ["id", "tenant_id"]),
        composite_fk("clinical_supervision", "fk_cs_patient_tenant", ["patient_id", "tenant_id"],
                     "patient", ["id", "tenant_id"]),
        composite_fk("clinical_supervision", "fk_cs_supervisor_tenant", ["supervisor_membership_id", "tenant_id"],
                     "tenant_membership", ["id", "tenant_id"]),
        composite_fk("clinical_supervision", "fk_cs_therapist_tenant", ["therapist_membership_id", "tenant_id"],
                     "tenant_membership", ["id", "tenant_id"]),
        runtime_role_sql(PRIVILEGES, UNDO_PRIVILEGES),
    ]
