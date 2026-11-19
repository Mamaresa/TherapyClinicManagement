from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import CLINICAL_SUPERVISOR, THERAPIST
from apps.accounts.tenancy import TenantScopedMixin
from apps.audit import services as audit
from apps.audit.models import AuditEvent
from apps.patients import access
from apps.patients.models import ClinicalAssignment, ClinicalSupervision, Patient

from .serializers import AssignmentSerializer, PatientSerializer, SupervisionSerializer


class PatientViewSet(TenantScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Patient.objects.order_by("last_name", "first_name")
    serializer_class = PatientSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return super().get_queryset().filter(access.visible_patients_q(self.request.membership))

    def check_permissions(self, request):
        super().check_permissions(request)
        if self.action in ("create", "partial_update") and not access.can_manage_patients(request.membership):
            audit.deny(request, action=f"patient.{self.action}", resource_type="patient",
                       resource_id=self.kwargs.get("pk"), reason="operational_access_required")


def _end(request, row, action_name, resource_type):
    if row.ended_at is not None:
        raise serializers.ValidationError("Already ended.")
    with transaction.atomic():
        row.ended_at = timezone.now()
        # The runtime database role may only UPDATE ended_at on these tables.
        row.save(update_fields=["ended_at"])
        audit.record(request, action=action_name, outcome=AuditEvent.SUCCESS,
                     resource_type=resource_type, resource_id=row.pk)


class CareTeamViewSet(TenantScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Shared rules: only an owner/admin manages the care team; every change is audited."""

    resource_type = ""

    def check_permissions(self, request):
        super().check_permissions(request)
        if not access.can_manage_care_team(request.membership):
            audit.deny(request, action=f"{self.resource_type}.{self.action}", resource_type=self.resource_type,
                       resource_id=self.kwargs.get("pk"), reason="owner_admin_required")

    def save_audited(self, serializer, metadata):
        try:
            with transaction.atomic():
                row = serializer.save(tenant=self.request.tenant)
                audit.record(self.request, action=f"{self.resource_type}.create", outcome=AuditEvent.SUCCESS,
                             resource_type=self.resource_type, resource_id=row.pk, metadata=metadata)
        except IntegrityError:
            raise serializers.ValidationError("This conflicts with an existing active record.")

    def require_role(self, membership, role, reason):
        if not membership.has_role(role):
            audit.deny(self.request, action=f"{self.resource_type}.create", resource_type="tenant_membership",
                       resource_id=membership.pk, reason=reason)

    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        row = self.get_object()
        _end(request, row, f"{self.resource_type}.end", self.resource_type)
        return Response(self.get_serializer(row).data)


class AssignmentViewSet(CareTeamViewSet):
    queryset = ClinicalAssignment.objects.order_by("started_at")
    serializer_class = AssignmentSerializer
    resource_type = "clinical_assignment"

    def perform_create(self, serializer):
        data = serializer.validated_data
        therapist = data["therapist_membership"]
        self.require_role(therapist, THERAPIST, "target_not_therapist")
        self.save_audited(serializer, {
            "patient": str(data["patient"].pk),
            "therapist_membership": str(therapist.pk),
            "role_in_case": data["role_in_case"],
            "self_assignment": therapist.pk == self.request.membership.pk,
        })


class SupervisionViewSet(CareTeamViewSet):
    queryset = ClinicalSupervision.objects.order_by("started_at")
    serializer_class = SupervisionSerializer
    resource_type = "clinical_supervision"

    def perform_create(self, serializer):
        data = serializer.validated_data
        supervisor, therapist, patient = data["supervisor_membership"], data["therapist_membership"], data["patient"]
        self.require_role(supervisor, CLINICAL_SUPERVISOR, "target_not_supervisor")
        if not ClinicalAssignment.objects.filter(
            tenant=self.request.tenant, patient=patient, therapist_membership=therapist, ended_at__isnull=True
        ).exists():
            raise serializers.ValidationError("The therapist is not actively assigned to this patient.")
        self.save_audited(serializer, {
            "patient": str(patient.pk),
            "supervisor_membership": str(supervisor.pk),
            "therapist_membership": str(therapist.pk),
            "self_assignment": supervisor.pk == self.request.membership.pk,
        })
