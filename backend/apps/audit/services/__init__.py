from rest_framework.exceptions import PermissionDenied

from apps.audit.models import AuditEvent


def record(request, *, action, outcome, resource_type, resource_id=None, tenant=None, metadata=None):
    """Write one audit event for the current user.

    Call it inside the same transaction as the change it records, so either
    both are stored or neither is.
    """
    membership = getattr(request, "membership", None)
    return AuditEvent.objects.create(
        tenant=tenant if tenant is not None else getattr(request, "tenant", None),
        actor_type=AuditEvent.USER,
        actor_user=request.user,
        actor_membership=membership,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        metadata=metadata or {},
    )


def deny(request, *, action, resource_type, reason, resource_id=None):
    """Record a denied attempt, then reject the request with 403.

    Call it before opening any transaction.atomic() block. Requests are not
    wrapped in a transaction (ATOMIC_REQUESTS is off), so the denial record is
    committed immediately and is not lost when the request fails.
    reason is a short fixed code (for example "self_role_change"), never free text.
    """
    record(
        request,
        action=action,
        outcome=AuditEvent.DENIED,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata={"reason": reason},
    )
    raise PermissionDenied(reason)
