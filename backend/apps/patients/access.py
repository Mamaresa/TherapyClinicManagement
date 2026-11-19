"""Who may see and manage patients (features.md 6.2 / 6.3).

Plain functions over a TenantMembership; no framework. Clinical supervision
is read only from ClinicalSupervision (the single source of truth, issue N4).
"""

from django.db.models import Q

from apps.accounts.models import ASSISTANT, CLINICAL_SUPERVISOR, OWNER_ADMIN, RECEPTIONIST_OPERATIONAL_ACCESS
from apps.patients.models import ClinicalAssignment, ClinicalSupervision


def can_manage_patients(membership):
    """Operational access: create and edit demographics, see every patient."""
    if membership.has_role(OWNER_ADMIN):
        return True
    return membership.has_role(ASSISTANT) and membership.has_grant(RECEPTIONIST_OPERATIONAL_ACCESS)


def can_manage_care_team(membership):
    """Create or end clinical assignments and supervisions."""
    return membership.has_role(OWNER_ADMIN)


def visible_patients_q(membership):
    """Filter for the patients this member may see (within the active tenant)."""
    if can_manage_patients(membership):
        return Q()
    assigned = ClinicalAssignment.objects.filter(
        therapist_membership=membership, ended_at__isnull=True
    ).values("patient_id")
    q = Q(pk__in=assigned)
    if membership.has_role(CLINICAL_SUPERVISOR):
        supervised = ClinicalSupervision.objects.filter(
            supervisor_membership=membership, ended_at__isnull=True
        ).values("patient_id")
        q |= Q(pk__in=supervised)
    return q
