from rest_framework import serializers

from apps.accounts.models import GRANT_CHOICES, ROLES, MembershipGrant, TenantMembership
from apps.accounts.tenancy import TenantScopedRelatedField

# Security rule for every serializer: tenant, user, author/actor and timestamp
# fields are read-only and set by the server. Fields are always listed explicitly.


class TenantSwitchSerializer(serializers.Serializer):
    tenant = serializers.UUIDField()


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    roles = serializers.ListField(child=serializers.ChoiceField(choices=ROLES), allow_empty=False)

    class Meta:
        model = TenantMembership
        fields = ["id", "user_email", "user_full_name", "roles", "joined_at", "ended_at"]
        read_only_fields = ["id", "joined_at", "ended_at"]

    def validate_roles(self, roles):
        if len(set(roles)) != len(roles):
            raise serializers.ValidationError("Duplicate roles.")
        return sorted(roles)

    def update(self, instance, validated_data):
        # The runtime database role may only UPDATE roles and ended_at here.
        instance.roles = validated_data.get("roles", instance.roles)
        instance.save(update_fields=["roles"])
        return instance


class GrantSerializer(serializers.ModelSerializer):
    membership = TenantScopedRelatedField(queryset=TenantMembership.objects.filter(ended_at__isnull=True))
    grant_code = serializers.ChoiceField(choices=GRANT_CHOICES)

    class Meta:
        model = MembershipGrant
        fields = ["id", "membership", "grant_code", "granted_at", "revoked_at"]
        read_only_fields = ["id", "granted_at", "revoked_at"]
