from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import OWNER_ADMIN, MembershipGrant, Tenant, TenantMembership
from apps.accounts.tenancy import SESSION_KEY, TenantScopedMixin, resolve_active_membership
from apps.audit import services as audit
from apps.audit.models import AuditEvent

from .serializers import GrantSerializer, MembershipSerializer, TenantSwitchSerializer


class ActiveTenantView(APIView):
    """GET: the active tenant. POST {"tenant": id}: switch, only into a tenant
    where the user has an active membership."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        membership = resolve_active_membership(request)
        if membership is None:
            return Response({"tenant": None, "roles": []})
        return Response({"tenant": str(membership.tenant_id), "roles": membership.roles})

    def post(self, request):
        data = TenantSwitchSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        tenant_id = data.validated_data["tenant"]
        membership = (
            TenantMembership.objects.select_related("tenant")
            .filter(user=request.user, tenant_id=tenant_id, ended_at__isnull=True, tenant__status=Tenant.ACTIVE)
            .first()
        )
        if membership is None:
            request.session.pop(SESSION_KEY, None)
            audit.deny(request, action="tenant.switch", resource_type="tenant", resource_id=tenant_id,
                       reason="no_active_membership")
        request.session.cycle_key()
        request.session[SESSION_KEY] = str(membership.tenant_id)
        request.membership, request.tenant = membership, membership.tenant
        audit.record(request, action="tenant.switch", outcome=AuditEvent.SUCCESS,
                     resource_type="tenant", resource_id=membership.tenant_id)
        return Response({"tenant": str(membership.tenant_id), "roles": membership.roles})


def require_owner_admin(request, action, resource_type, resource_id=None):
    if not request.membership.has_role(OWNER_ADMIN):
        audit.deny(request, action=action, resource_type=resource_type, resource_id=resource_id,
                   reason="owner_admin_required")


class MembershipViewSet(TenantScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Members of the active tenant. Only an owner/admin may change roles, and
    never their own."""

    queryset = TenantMembership.objects.select_related("user").order_by("joined_at")
    serializer_class = MembershipSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        require_owner_admin(request, f"membership.{self.action}", "tenant_membership", kwargs.get("pk"))

    def perform_update(self, serializer):
        target = serializer.instance
        if target.pk == self.request.membership.pk:
            audit.deny(self.request, action="membership.roles_change", resource_type="tenant_membership",
                       resource_id=target.pk, reason="self_role_change")
        if target.ended_at is not None:
            raise serializers.ValidationError("This membership has ended.")
        old_roles = list(target.roles)
        with transaction.atomic():
            serializer.save()
            audit.record(self.request, action="membership.roles_change", outcome=AuditEvent.SUCCESS,
                         resource_type="tenant_membership", resource_id=target.pk,
                         metadata={"old_roles": old_roles, "new_roles": serializer.instance.roles})


class GrantViewSet(TenantScopedMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Optional grants. Only an owner/admin may grant or revoke, and never for
    their own membership. DELETE revokes (sets revoked_at); rows are kept."""

    queryset = MembershipGrant.objects.filter(revoked_at__isnull=True).order_by("granted_at")
    serializer_class = GrantSerializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        require_owner_admin(request, f"grant.{self.action}", "membership_grant", kwargs.get("pk"))

    def perform_create(self, serializer):
        target = serializer.validated_data["membership"]
        if target.pk == self.request.membership.pk:
            audit.deny(self.request, action="grant.create", resource_type="tenant_membership",
                       resource_id=target.pk, reason="self_grant")
        try:
            with transaction.atomic():
                grant = serializer.save(tenant=self.request.tenant)
                audit.record(self.request, action="grant.create", outcome=AuditEvent.SUCCESS,
                             resource_type="membership_grant", resource_id=grant.pk,
                             metadata={"membership": str(target.pk), "grant_code": grant.grant_code})
        except IntegrityError:
            raise serializers.ValidationError("This grant is already active.")

    def destroy(self, request, *args, **kwargs):
        grant = self.get_object()
        if grant.membership_id == request.membership.pk:
            audit.deny(request, action="grant.revoke", resource_type="membership_grant",
                       resource_id=grant.pk, reason="self_grant")
        with transaction.atomic():
            grant.revoked_at = timezone.now()
            grant.save(update_fields=["revoked_at"])
            audit.record(request, action="grant.revoke", outcome=AuditEvent.SUCCESS,
                         resource_type="membership_grant", resource_id=grant.pk,
                         metadata={"membership": str(grant.membership_id), "grant_code": grant.grant_code})
        return Response(status=status.HTTP_204_NO_CONTENT)
