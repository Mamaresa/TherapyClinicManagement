"""N3: users cannot raise their own privileges or give themselves clinical access."""

import pytest

from apps.accounts.models import MembershipGrant, TenantMembership
from apps.audit.models import AuditEvent
from apps.patients.models import ClinicalAssignment, ClinicalSupervision, Patient

from .conftest import assign, client_for, make_member

pytestmark = pytest.mark.django_db


def denied(user, reason):
    return AuditEvent.objects.filter(outcome="denied", actor_user=user, metadata__reason=reason).exists()


def test_owner_admin_cannot_change_own_roles(world):
    admin = world["admin_a"]
    response = client_for(admin).patch(f"/api/v1/memberships/{admin.pk}/",
                                       {"roles": ["owner_admin", "therapist"]}, format="json")
    assert response.status_code == 403
    admin.refresh_from_db()
    assert admin.roles == ["owner_admin"]
    assert denied(admin.user, "self_role_change")


def test_non_admin_cannot_change_own_or_other_roles(world):
    therapist = world["therapist_a"]
    client = client_for(therapist)
    for target in (therapist, world["therapist2_a"]):
        response = client.patch(f"/api/v1/memberships/{target.pk}/", {"roles": ["owner_admin"]}, format="json")
        assert response.status_code == 403
        target.refresh_from_db()
        assert target.roles == ["therapist"]
    assert AuditEvent.objects.filter(outcome="denied", actor_user=therapist.user,
                                     metadata__reason="owner_admin_required").count() == 2


def test_owner_admin_can_change_another_members_roles_and_it_is_audited(world):
    target = world["therapist_a"]
    response = client_for(world["admin_a"]).patch(f"/api/v1/memberships/{target.pk}/",
                                                  {"roles": ["therapist", "clinical_supervisor"]}, format="json")
    assert response.status_code == 200, response.content
    target.refresh_from_db()
    assert target.roles == ["clinical_supervisor", "therapist"]
    event = AuditEvent.objects.get(action="membership.roles_change", outcome="success")
    assert event.resource_id == target.pk
    assert event.metadata == {"old_roles": ["therapist"], "new_roles": ["clinical_supervisor", "therapist"]}


def test_nobody_can_grant_themselves_extra_privileges(world):
    for member, reason in [(world["assistant_a"], "owner_admin_required"), (world["admin_a"], "self_grant")]:
        response = client_for(member).post("/api/v1/grants/", {
            "membership": str(member.pk), "grant_code": "receptionist_operational_access",
        }, format="json")
        assert response.status_code == 403
        assert denied(member.user, reason)
    assert not MembershipGrant.objects.exists()


def test_owner_admin_grants_and_revokes_for_others_with_audit(world):
    client = client_for(world["admin_a"])
    response = client.post("/api/v1/grants/", {
        "membership": str(world["assistant_a"].pk), "grant_code": "receptionist_operational_access",
    }, format="json")
    assert response.status_code == 201, response.content
    assert client.delete(f"/api/v1/grants/{response.json()['id']}/").status_code == 204
    grant = MembershipGrant.objects.get()
    assert grant.revoked_at is not None
    assert set(AuditEvent.objects.filter(outcome="success").values_list("action", flat=True)) == {
        "grant.create", "grant.revoke"}


@pytest.mark.parametrize("who", ["therapist_a", "assistant_a", "supervisor_a"])
def test_non_admins_cannot_assign_themselves_to_a_patient(world, who):
    member = world[who]
    response = client_for(member).post("/api/v1/assignments/", {
        "patient": str(world["patient_a"].pk), "therapist_membership": str(member.pk), "role_in_case": "primary",
    }, format="json")
    assert response.status_code == 403
    assert not ClinicalAssignment.objects.exists()
    assert denied(member.user, "owner_admin_required")


def test_owner_admin_without_therapist_role_cannot_assign_themselves(world):
    admin = world["admin_a"]
    response = client_for(admin).post("/api/v1/assignments/", {
        "patient": str(world["patient_a"].pk), "therapist_membership": str(admin.pk), "role_in_case": "primary",
    }, format="json")
    assert response.status_code == 403
    assert not ClinicalAssignment.objects.exists()
    assert denied(admin.user, "target_not_therapist")


def test_owner_admin_assigns_a_therapist_and_it_is_audited(world):
    response = client_for(world["admin_a"]).post("/api/v1/assignments/", {
        "patient": str(world["patient_a"].pk), "therapist_membership": str(world["therapist_a"].pk),
        "role_in_case": "primary",
    }, format="json")
    assert response.status_code == 201, response.content
    event = AuditEvent.objects.get(action="clinical_assignment.create", outcome="success")
    assert event.metadata["self_assignment"] is False


def test_solo_practitioner_self_assignment_is_allowed_but_flagged(world):
    solo = make_member(world["a"], "solo@a.test", ["owner_admin", "therapist"])
    response = client_for(solo).post("/api/v1/assignments/", {
        "patient": str(world["patient_a"].pk), "therapist_membership": str(solo.pk), "role_in_case": "primary",
    }, format="json")
    assert response.status_code == 201, response.content
    assert AuditEvent.objects.get(action="clinical_assignment.create").metadata["self_assignment"] is True


def test_supervisor_cannot_give_themselves_supervision(world):
    assign(world["patient_a"], world["therapist_a"])
    supervisor = world["supervisor_a"]
    response = client_for(supervisor).post("/api/v1/supervisions/", {
        "patient": str(world["patient_a"].pk), "supervisor_membership": str(supervisor.pk),
        "therapist_membership": str(world["therapist_a"].pk),
    }, format="json")
    assert response.status_code == 403
    assert not ClinicalSupervision.objects.exists()
    assert denied(supervisor.user, "owner_admin_required")


def test_sensitive_fields_in_request_bodies_are_ignored(world):
    client = client_for(world["admin_a"])
    other_tenant = str(world["b"].pk)
    old = "2000-01-01T00:00:00Z"

    target = world["therapist_a"]
    response = client.patch(f"/api/v1/memberships/{target.pk}/", {
        "roles": ["therapist"], "tenant": other_tenant, "user": str(world["admin_a"].user_id),
        "user_email": "evil@x.test", "joined_at": old, "ended_at": old,
    }, format="json")
    assert response.status_code == 200, response.content
    fresh = TenantMembership.objects.get(pk=target.pk)
    assert (fresh.tenant_id, fresh.user_id, fresh.ended_at) == (world["a"].pk, target.user_id, None)
    assert fresh.joined_at == target.joined_at

    response = client.post("/api/v1/patients/", {
        "first_name": "X", "last_name": "Y", "tenant": other_tenant, "status": "archived",
    }, format="json")
    patient = Patient.objects.get(pk=response.json()["id"])
    assert (patient.tenant_id, patient.status) == (world["a"].pk, "active")

    response = client.post("/api/v1/assignments/", {
        "patient": str(world["patient_a"].pk), "therapist_membership": str(target.pk), "role_in_case": "primary",
        "tenant": other_tenant, "started_at": old, "ended_at": old,
    }, format="json")
    row = ClinicalAssignment.objects.get(pk=response.json()["id"])
    assert row.tenant_id == world["a"].pk and row.ended_at is None and row.started_at.year > 2000

    response = client.post("/api/v1/grants/", {
        "membership": str(world["assistant_a"].pk), "grant_code": "security_metadata_review",
        "tenant": other_tenant, "revoked_at": old,
    }, format="json")
    grant = MembershipGrant.objects.get(pk=response.json()["id"])
    assert grant.tenant_id == world["a"].pk and grant.revoked_at is None
