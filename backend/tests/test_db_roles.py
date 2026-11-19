"""N1: the runtime database role cannot bypass database-level protections.

Every test here runs as the restricted runtime role (see conftest.py).
"""

import pytest
from django.conf import settings
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from apps.accounts.models import MembershipGrant
from apps.audit.models import AuditEvent

from .conftest import assign, client_for

pytestmark = pytest.mark.django_db

PROTECTED_TABLES = [
    "audit_event", "patient", "clinical_assignment", "clinical_supervision",
    "tenant_membership", "membership_grant", "app_user", "tenant",
]


def fetch(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def must_fail(sql, params=None):
    with pytest.raises(DatabaseError) as exc:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
    return str(exc.value)


@pytest.fixture
def event(world):
    return AuditEvent.objects.create(
        tenant=world["a"], actor_type="user", actor_user=world["admin_a"].user,
        action="test.event", resource_type="patient", outcome="success",
    )


def test_tests_run_as_the_restricted_runtime_role():
    assert fetch("SELECT current_user")[0] == settings.DB_RUNTIME_ROLE
    flags = fetch(
        "SELECT rolsuper, rolcreaterole, rolcreatedb, rolbypassrls, rolreplication "
        "FROM pg_roles WHERE rolname = current_user"
    )
    assert flags == (False, False, False, False, False)


def test_runtime_role_owns_no_tables_or_functions():
    tables = fetch(
        "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = 'public' AND c.relowner = (SELECT oid FROM pg_roles WHERE rolname = current_user)"
    )[0]
    functions = fetch(
        "SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
        "WHERE n.nspname = 'public' AND p.proowner = (SELECT oid FROM pg_roles WHERE rolname = current_user)"
    )[0]
    assert (tables, functions) == (0, 0)


def test_runtime_role_can_insert_and_read_audit_events(event):
    assert AuditEvent.objects.filter(pk=event.pk).exists()


def test_runtime_role_cannot_update_audit_events(event):
    assert "permission denied" in must_fail("UPDATE audit_event SET action = 'x' WHERE id = %s", [event.pk])
    with pytest.raises(DatabaseError), transaction.atomic():
        AuditEvent.objects.filter(pk=event.pk).update(outcome="denied")
    event.refresh_from_db()
    assert (event.action, event.outcome) == ("test.event", "success")


def test_runtime_role_cannot_delete_audit_events(event):
    assert "permission denied" in must_fail("DELETE FROM audit_event WHERE id = %s", [event.pk])
    with pytest.raises(DatabaseError), transaction.atomic():
        AuditEvent.objects.filter(pk=event.pk).delete()
    assert AuditEvent.objects.filter(pk=event.pk).exists()


@pytest.mark.parametrize("table", PROTECTED_TABLES)
def test_runtime_role_cannot_truncate(table):
    assert "permission denied" in must_fail(f"TRUNCATE {table}")


@pytest.mark.parametrize("table", ["patient", "clinical_assignment", "clinical_supervision",
                                   "tenant_membership", "membership_grant", "app_user", "tenant"])
def test_runtime_role_cannot_delete_history(world, table):
    assert "permission denied" in must_fail(f"DELETE FROM {table}")


@pytest.mark.parametrize("sql", [
    "ALTER TABLE audit_event DISABLE TRIGGER ALL",
    "ALTER TABLE audit_event DISABLE TRIGGER audit_event_append_only",
    "DROP TRIGGER audit_event_append_only ON audit_event",
    "ALTER TABLE audit_event ADD COLUMN extra integer",
    "ALTER TABLE audit_event OWNER TO CURRENT_USER",
    "ALTER TABLE clinical_assignment DROP CONSTRAINT fk_ca_patient_tenant",
    "DROP TABLE audit_event",
    "DROP FUNCTION forbid_change()",
    "CREATE OR REPLACE FUNCTION forbid_change() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END $$",
    "CREATE TRIGGER sneaky BEFORE INSERT ON patient FOR EACH ROW EXECUTE FUNCTION forbid_change()",
    "CREATE TABLE sneaky (id integer)",
    "SET session_replication_role = replica",
])
def test_runtime_role_cannot_change_schema_or_disable_protections(sql):
    message = must_fail(sql)
    assert "must be owner" in message or "permission denied" in message


def test_append_only_triggers_exist_and_fire_always():
    rows = connection.cursor()
    rows.execute(
        "SELECT tgname, tgenabled FROM pg_trigger "
        "WHERE tgrelid = 'audit_event'::regclass AND NOT tgisinternal ORDER BY tgname"
    )
    assert rows.fetchall() == [("audit_event_append_only", "A"), ("audit_event_no_truncate", "A")]


def test_care_team_history_cannot_be_rewritten(world):
    row = assign(world["patient_a"], world["therapist_a"])
    msg = must_fail("UPDATE clinical_assignment SET therapist_membership_id = %s WHERE id = %s",
                    [world["therapist2_a"].pk, row.pk])
    assert "permission denied" in msg
    with pytest.raises(DatabaseError), transaction.atomic():
        row.save()  # a full-row UPDATE touches protected columns
    row.ended_at = timezone.now()
    row.save(update_fields=["ended_at"])  # ending an assignment is allowed
    row.refresh_from_db()
    assert row.ended_at is not None and row.therapist_membership_id == world["therapist_a"].pk


def test_membership_and_grant_history_cannot_be_rewritten(world):
    member = world["therapist_a"]
    assert "permission denied" in must_fail(
        "UPDATE tenant_membership SET user_id = %s WHERE id = %s", [world["admin_a"].user_id, member.pk]
    )
    member.roles = ["therapist", "clinical_supervisor"]
    member.save(update_fields=["roles"])  # role changes themselves are allowed
    grant = MembershipGrant.objects.create(
        tenant=world["a"], membership=world["assistant_a"], grant_code="receptionist_operational_access"
    )
    assert "permission denied" in must_fail(
        "UPDATE membership_grant SET grant_code = 'security_metadata_review' WHERE id = %s", [grant.pk]
    )


def test_normal_application_operations_work_as_runtime_role(world):
    admin = client_for(world["admin_a"])
    assert admin.post("/api/v1/session/tenant/", {"tenant": str(world["a"].pk)}, format="json").status_code == 200
    patient = admin.post("/api/v1/patients/", {"first_name": "Reza", "last_name": "Moradi"}, format="json")
    assert patient.status_code == 201, patient.content
    pid = patient.json()["id"]
    assert admin.patch(f"/api/v1/patients/{pid}/", {"last_name": "Moradi-Nia"}, format="json").status_code == 200
    created = admin.post("/api/v1/assignments/", {
        "patient": pid, "therapist_membership": str(world["therapist_a"].pk), "role_in_case": "primary",
    }, format="json")
    assert created.status_code == 201, created.content
    assert admin.post(f"/api/v1/assignments/{created.json()['id']}/end/").status_code == 200
    assert admin.patch(f"/api/v1/memberships/{world['therapist_a'].pk}/",
                       {"roles": ["therapist", "clinical_supervisor"]}, format="json").status_code == 200
    grant = admin.post("/api/v1/grants/", {
        "membership": str(world["assistant_a"].pk), "grant_code": "receptionist_operational_access",
    }, format="json")
    assert grant.status_code == 201, grant.content
    assert admin.delete(f"/api/v1/grants/{grant.json()['id']}/").status_code == 204
    assert AuditEvent.objects.filter(outcome="success").count() >= 6
