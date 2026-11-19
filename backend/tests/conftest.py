import pytest
from django.conf import settings
from django.db import connections
from rest_framework.test import APIClient

from apps.accounts.models import Tenant, TenantMembership, User
from apps.accounts.tenancy import SESSION_KEY
from apps.patients.models import ClinicalAssignment, Patient


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Create and migrate the test database as the owner role, then run every
    test as the restricted runtime role, exactly like production."""
    conn = connections["default"]
    owner = (conn.settings_dict["USER"], conn.settings_dict["PASSWORD"])
    conn.close()
    conn.settings_dict["USER"] = settings.RUNTIME_DATABASE["USER"]
    conn.settings_dict["PASSWORD"] = settings.RUNTIME_DATABASE["PASSWORD"]
    yield
    conn.close()
    conn.settings_dict["USER"], conn.settings_dict["PASSWORD"] = owner


def make_tenant(slug):
    return Tenant.objects.create(name=slug.title(), slug=slug)


def make_member(tenant, email, roles):
    user = User.objects.create_user(email=email, password="pw", full_name=email.split("@")[0])
    return TenantMembership.objects.create(tenant=tenant, user=user, roles=roles)


def make_patient(tenant, first="Sara", last="Ahmadi"):
    return Patient.objects.create(tenant=tenant, first_name=first, last_name=last)


def assign(patient, therapist, role="primary"):
    return ClinicalAssignment.objects.create(
        tenant=patient.tenant, patient=patient, therapist_membership=therapist, role_in_case=role
    )


def client_for(membership):
    """Logged-in API client with the membership's tenant selected in the session."""
    client = APIClient()
    client.force_login(membership.user)
    session = client.session
    session[SESSION_KEY] = str(membership.tenant_id)
    session.save()
    return client


@pytest.fixture
def world(db):
    """Two clinics with the usual staff, one patient each."""
    a, b = make_tenant("clinic-a"), make_tenant("clinic-b")
    w = {
        "a": a,
        "b": b,
        "admin_a": make_member(a, "admin@a.test", ["owner_admin"]),
        "therapist_a": make_member(a, "therapist@a.test", ["therapist"]),
        "therapist2_a": make_member(a, "therapist2@a.test", ["therapist"]),
        "supervisor_a": make_member(a, "supervisor@a.test", ["clinical_supervisor"]),
        "assistant_a": make_member(a, "assistant@a.test", ["assistant"]),
        "admin_b": make_member(b, "admin@b.test", ["owner_admin"]),
        "therapist_b": make_member(b, "therapist@b.test", ["therapist"]),
    }
    w["patient_a"] = make_patient(a, "Ali", "Rezaei")
    w["patient_b"] = make_patient(b, "Mina", "Karimi")
    return w
