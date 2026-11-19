"""N4: ClinicalSupervision is the only source of truth for clinical supervision."""

import pytest
from django.db import IntegrityError, connection, transaction

from apps.patients.models import ClinicalAssignment, ClinicalSupervision

from .conftest import assign, client_for

pytestmark = pytest.mark.django_db


def test_clinical_assignment_has_no_supervisor_column():
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'clinical_assignment'")
        columns = {row[0] for row in cursor.fetchall()}
    assert columns and not any("supervisor" in name for name in columns)
    assert not any("supervisor" in f.name for f in ClinicalAssignment._meta.get_fields())


def test_supervisor_access_comes_only_from_clinical_supervision(world):
    admin = client_for(world["admin_a"])
    supervisor = client_for(world["supervisor_a"])
    patient = str(world["patient_a"].pk)
    assign(world["patient_a"], world["therapist_a"])
    assert supervisor.get("/api/v1/patients/").json() == []

    created = admin.post("/api/v1/supervisions/", {
        "patient": patient, "supervisor_membership": str(world["supervisor_a"].pk),
        "therapist_membership": str(world["therapist_a"].pk),
    }, format="json")
    assert created.status_code == 201, created.content
    assert [p["id"] for p in supervisor.get("/api/v1/patients/").json()] == [patient]

    assert admin.post(f"/api/v1/supervisions/{created.json()['id']}/end/").status_code == 200
    assert supervisor.get("/api/v1/patients/").json() == []
    assert supervisor.get(f"/api/v1/patients/{patient}/").status_code == 404


def test_supervision_requires_the_therapist_to_be_assigned(world):
    response = client_for(world["admin_a"]).post("/api/v1/supervisions/", {
        "patient": str(world["patient_a"].pk), "supervisor_membership": str(world["supervisor_a"].pk),
        "therapist_membership": str(world["therapist_a"].pk),
    }, format="json")
    assert response.status_code == 400
    assert not ClinicalSupervision.objects.exists()


def test_a_member_cannot_supervise_their_own_case(world):
    world["therapist_a"].roles = ["therapist", "clinical_supervisor"]
    world["therapist_a"].save(update_fields=["roles"])
    assign(world["patient_a"], world["therapist_a"])
    response = client_for(world["admin_a"]).post("/api/v1/supervisions/", {
        "patient": str(world["patient_a"].pk), "supervisor_membership": str(world["therapist_a"].pk),
        "therapist_membership": str(world["therapist_a"].pk),
    }, format="json")
    assert response.status_code == 400
    with pytest.raises(IntegrityError), transaction.atomic():  # the database refuses it too
        ClinicalSupervision.objects.create(tenant=world["a"], patient=world["patient_a"],
                                           supervisor_membership=world["therapist_a"],
                                           therapist_membership=world["therapist_a"])
