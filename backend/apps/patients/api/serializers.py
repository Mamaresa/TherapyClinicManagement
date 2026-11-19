from rest_framework import serializers

from apps.accounts.models import TenantMembership
from apps.accounts.tenancy import TenantScopedRelatedField
from apps.patients.models import ClinicalAssignment, ClinicalSupervision, Patient

# tenant is never a serializer field; it comes from the active session.

ACTIVE_MEMBERSHIPS = TenantMembership.objects.filter(ended_at__isnull=True)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "first_name", "last_name", "dob", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class AssignmentSerializer(serializers.ModelSerializer):
    patient = TenantScopedRelatedField(queryset=Patient.objects.all())
    therapist_membership = TenantScopedRelatedField(queryset=ACTIVE_MEMBERSHIPS)

    class Meta:
        model = ClinicalAssignment
        fields = ["id", "patient", "therapist_membership", "role_in_case", "started_at", "ended_at"]
        read_only_fields = ["id", "started_at", "ended_at"]


class SupervisionSerializer(serializers.ModelSerializer):
    patient = TenantScopedRelatedField(queryset=Patient.objects.all())
    supervisor_membership = TenantScopedRelatedField(queryset=ACTIVE_MEMBERSHIPS)
    therapist_membership = TenantScopedRelatedField(queryset=ACTIVE_MEMBERSHIPS)

    class Meta:
        model = ClinicalSupervision
        fields = ["id", "patient", "supervisor_membership", "therapist_membership", "started_at", "ended_at"]
        read_only_fields = ["id", "started_at", "ended_at"]

    def validate(self, attrs):
        if attrs["supervisor_membership"] == attrs["therapist_membership"]:
            raise serializers.ValidationError("The supervisor cannot supervise themselves.")
        return attrs
