from django.db import models
from django.db.models import F, Q

from apps.core.models import TenantScopedModel


class Patient(TenantScopedModel):
    """A person receiving care at one clinic.

    Only the columns needed so far exist. Contact, intake and normalized-name
    columns from the schema design are added with the patient-management feature.
    """

    ACTIVE, ARCHIVED = "active", "archived"

    first_name = models.TextField()
    last_name = models.TextField()
    dob = models.DateField(null=True, blank=True)
    status = models.TextField(choices=[(ACTIVE, "Active"), (ARCHIVED, "Archived")], default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "patient"
        constraints = [
            *TenantScopedModel.Meta.constraints,
            models.CheckConstraint(
                condition=Q(status="active") | Q(archived_at__isnull=False), name="ck_patient_archived"
            ),
        ]


class ClinicalAssignment(TenantScopedModel):
    """Which therapist treats a patient, in which role, and when.

    Supervision is deliberately NOT stored here: ClinicalSupervision is the
    only source of truth for clinical supervision (issue N4).
    Rows are history: the runtime role may only update ended_at.
    """

    PRIMARY, CO_THERAPIST, OBSERVING = "primary", "co_therapist", "observing"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="assignments")
    therapist_membership = models.ForeignKey(
        "accounts.TenantMembership", on_delete=models.PROTECT, related_name="assignments"
    )
    role_in_case = models.TextField(
        choices=[(PRIMARY, "Primary"), (CO_THERAPIST, "Co-therapist"), (OBSERVING, "Observing")]
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clinical_assignment"
        constraints = [
            *TenantScopedModel.Meta.constraints,
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("started_at")), name="ck_ca_dates"
            ),
            models.UniqueConstraint(
                fields=["patient"],
                condition=Q(role_in_case="primary", ended_at__isnull=True),
                name="uq_ca_one_active_primary",
            ),
            models.UniqueConstraint(
                fields=["patient", "therapist_membership"],
                condition=Q(ended_at__isnull=True),
                name="uq_ca_active_pair",
            ),
        ]


class ClinicalSupervision(TenantScopedModel):
    """The single source of truth for clinical supervision (issue N4).

    Gives one supervisor clinical access to one specific patient, supervised
    through the therapist treating that patient.
    Rows are history: the runtime role may only update ended_at.
    """

    supervisor_membership = models.ForeignKey(
        "accounts.TenantMembership", on_delete=models.PROTECT, related_name="supervisions"
    )
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="supervisions")
    therapist_membership = models.ForeignKey(
        "accounts.TenantMembership", on_delete=models.PROTECT, related_name="supervised_cases"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clinical_supervision"
        constraints = [
            *TenantScopedModel.Meta.constraints,
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("started_at")), name="ck_cs_dates"
            ),
            models.CheckConstraint(
                condition=~Q(supervisor_membership=F("therapist_membership")), name="ck_cs_no_self"
            ),
            models.UniqueConstraint(
                fields=["supervisor_membership", "patient"],
                condition=Q(ended_at__isnull=True),
                name="uq_cs_active_pair",
            ),
        ]
