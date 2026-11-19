"""Tenant isolation for API reads and writes (issue N2).

One rule, enforced in one place:
- The active tenant is chosen with POST /api/v1/session/tenant/, checked
  against the user's active membership, and stored in the server-side session.
- Every request re-validates that membership (user active, membership not
  ended, tenant active). Tenant ids sent by the client in bodies, headers or
  query strings are never used for scoping.
- TenantScopedMixin filters every queryset by request.tenant and sets the
  tenant on create. TenantScopedRelatedField does the same for foreign keys
  that clients send in request bodies.
tests/test_tenant_isolation.py checks that every routed view over a
tenant-owned model uses TenantScopedMixin as its first base.
"""

from rest_framework import permissions, relations

from apps.accounts.models import Tenant, TenantMembership

SESSION_KEY = "active_tenant_id"


def resolve_active_membership(request):
    tenant_id = request.session.get(SESSION_KEY)
    if not tenant_id or not request.user or not request.user.is_authenticated:
        return None
    return (
        TenantMembership.objects.select_related("tenant", "user")
        .filter(
            user=request.user,
            tenant_id=tenant_id,
            ended_at__isnull=True,
            tenant__status=Tenant.ACTIVE,
        )
        .first()
    )


class HasActiveTenant(permissions.BasePermission):
    message = "No active tenant is selected, or your membership in it is no longer active."

    def has_permission(self, request, view):
        membership = resolve_active_membership(request)
        if membership is None:
            request.session.pop(SESSION_KEY, None)
            return False
        request.membership = membership
        request.tenant = membership.tenant
        return True


class TenantScopedMixin:
    """Must be the FIRST base of every API view over a tenant-owned model, e.g.
    class PatientViewSet(TenantScopedMixin, mixins.ListModelMixin, viewsets.GenericViewSet),
    so its perform_create wins over DRF's."""

    permission_classes = [permissions.IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return super().get_queryset().filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class TenantScopedRelatedField(relations.PrimaryKeyRelatedField):
    """A foreign key sent by the client; only rows of the active tenant resolve."""

    def get_queryset(self):
        return super().get_queryset().filter(tenant=self.context["request"].tenant)
