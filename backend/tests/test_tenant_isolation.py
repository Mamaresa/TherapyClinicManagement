"""N2: users of one tenant can never read or change another tenant's data."""

import pytest
from django.urls import get_resolver
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.test import APIClient

from apps.accounts.models import MembershipGrant, Tenant, TenantMembership
from apps.accounts.tenancy import TenantScopedMixin
from apps.audit.models import AuditEvent
from apps.patients.models import ClinicalAssignment, Patient

from .conftest import assign, client_for

pytestmark = pytest.mark.django_db


def ids(response):
    assert response.status_code == 200, response.content
    return {row["id"] for row in response.json()}


def test_list_shows_only_the_active_tenant(world):
    listed = ids(client_for(world["admin_a"]).get("/api/v1/patients/"))
    assert str(world["patient_a"].pk) in listed
    assert str(world["patient_b"].pk) not in listed


def test_other_tenant_record_by_id_is_not_found(world):
    client = client_for(world["admin_a"])
    other = world["patient_b"].pk
    assert client.get(f"/api/v1/patients/{other}/").status_code == 404
    assert client.get(f"/api/v1/memberships/{world['admin_b'].pk}/").status_code == 404
    row = assign(world["patient_b"], world["therapist_b"])
    assert client.get(f"/api/v1/assignments/{row.pk}/").status_code == 404


def test_other_tenant_records_cannot_be_modified_or_deleted(world):
    client = client_for(world["admin_a"])
    patient_b = world["patient_b"]
    response = client.patch(f"/api/v1/patients/{patient_b.pk}/", {"last_name": "Hacked"}, format="json")
    assert response.status_code == 404
    patient_b.refresh_from_db()
    assert patient_b.last_name == "Karimi"

    member_b = world["therapist_b"]
    response = client.patch(f"/api/v1/memberships/{member_b.pk}/", {"roles": ["owner_admin"]}, format="json")
    assert response.status_code == 404
    member_b.refresh_from_db()
    assert member_b.roles == ["therapist"]

    grant_b = MembershipGrant.objects.create(tenant=world["b"], membership=member_b,
                                             grant_code="security_metadata_review")
    assert client.delete(f"/api/v1/grants/{grant_b.pk}/").status_code == 404
    grant_b.refresh_from_db()
    assert grant_b.revoked_at is None

    row = assign(patient_b, member_b)
    assert client.post(f"/api/v1/assignments/{row.pk}/end/").status_code == 404
    row.refresh_from_db()
    assert row.ended_at is None


def test_request_bodies_cannot_reference_another_tenants_rows(world):
    client = client_for(world["admin_a"])
    for patient, therapist in [(world["patient_b"], world["therapist_a"]),
                               (world["patient_a"], world["therapist_b"])]:
        response = client.post("/api/v1/assignments/", {
            "patient": str(patient.pk), "therapist_membership": str(therapist.pk), "role_in_case": "primary",
        }, format="json")
        assert response.status_code == 400
    assert not ClinicalAssignment.objects.exists()
    response = client.post("/api/v1/grants/", {
        "membership": str(world["therapist_b"].pk), "grant_code": "security_metadata_review",
    }, format="json")
    assert response.status_code == 400
    assert not MembershipGrant.objects.exists()


def test_client_supplied_tenant_ids_are_ignored(world):
    client = client_for(world["admin_a"])
    b = str(world["b"].pk)
    response = client.post(f"/api/v1/patients/?tenant={b}", {"first_name": "New", "last_name": "Patient", "tenant": b},
                           format="json", HTTP_X_TENANT_ID=b)
    assert response.status_code == 201, response.content
    assert Patient.objects.get(pk=response.json()["id"]).tenant_id == world["a"].pk
    listed = ids(client.get(f"/api/v1/patients/?tenant={b}", HTTP_X_TENANT_ID=b))
    assert str(world["patient_b"].pk) not in listed


def test_switching_to_a_tenant_without_membership_is_denied_and_audited(world):
    client = client_for(world["admin_a"])
    response = client.post("/api/v1/session/tenant/", {"tenant": str(world["b"].pk)}, format="json")
    assert response.status_code == 403
    assert AuditEvent.objects.filter(action="tenant.switch", outcome="denied",
                                     resource_id=world["b"].pk, actor_user=world["admin_a"].user).exists()
    # A failed switch leaves no active tenant at all.
    assert client.get("/api/v1/patients/").status_code == 403


def test_switching_follows_the_users_real_memberships(world):
    user = world["therapist_a"].user
    member_b = TenantMembership.objects.create(tenant=world["b"], user=user, roles=["therapist"])
    assign(world["patient_a"], world["therapist_a"])
    assign(world["patient_b"], member_b)
    client = APIClient()
    client.force_login(user)
    assert client.get("/api/v1/patients/").status_code == 403  # no tenant selected yet
    assert client.post("/api/v1/session/tenant/", {"tenant": str(world["b"].pk)}, format="json").status_code == 200
    assert ids(client.get("/api/v1/patients/")) == {str(world["patient_b"].pk)}
    assert client.post("/api/v1/session/tenant/", {"tenant": str(world["a"].pk)}, format="json").status_code == 200
    assert ids(client.get("/api/v1/patients/")) == {str(world["patient_a"].pk)}


def test_ended_membership_or_suspended_tenant_loses_access_immediately(world):
    client = client_for(world["admin_a"])
    assert client.get("/api/v1/patients/").status_code == 200
    member = world["admin_a"]
    member.ended_at = timezone.now()
    member.save(update_fields=["ended_at"])
    assert client.get("/api/v1/patients/").status_code == 403
    assert client.post("/api/v1/session/tenant/", {"tenant": str(world["a"].pk)}, format="json").status_code == 403

    other = client_for(world["admin_b"])
    Tenant.objects.filter(pk=world["b"].pk).update(status="suspended")
    assert other.get("/api/v1/patients/").status_code == 403


def test_unauthenticated_requests_are_rejected(world):
    assert APIClient().get("/api/v1/patients/").status_code == 403


def _routed_views(patterns):
    for pattern in patterns:
        if hasattr(pattern, "url_patterns"):
            yield from _routed_views(pattern.url_patterns)
        elif getattr(pattern.callback, "cls", None):
            yield pattern.callback.cls


def test_every_view_over_tenant_data_is_tenant_scoped():
    """Guard for future endpoints: any routed view over a model with a tenant
    field must put TenantScopedMixin before DRF's mixins and must not expose
    tenant as a serializer field."""
    drf_bases = [mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                 mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet]
    checked = set()
    for view in _routed_views(get_resolver().url_patterns):
        queryset = getattr(view, "queryset", None)
        if queryset is None or "tenant" not in {f.name for f in queryset.model._meta.fields}:
            continue
        mro = view.__mro__
        assert TenantScopedMixin in mro, view
        for base in drf_bases:
            if base in mro:
                assert mro.index(TenantScopedMixin) < mro.index(base), (view, base)
        assert "tenant" not in view.serializer_class().fields, view
        checked.add(view.__name__)
    assert checked == {"PatientViewSet", "AssignmentViewSet", "SupervisionViewSet",
                       "MembershipViewSet", "GrantViewSet"}
