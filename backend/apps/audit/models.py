import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class AuditEvent(models.Model):
    """Append-only security log.

    The runtime database role has no UPDATE, DELETE or TRUNCATE on this table,
    and a trigger rejects those statements for every role (migration 0002).
    metadata must never contain clinical content, names or credentials.
    """

    USER, SYSTEM = "user", "system"
    SUCCESS, DENIED, ERROR = "success", "denied", "error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("accounts.Tenant", null=True, on_delete=models.PROTECT, related_name="+")
    actor_type = models.TextField(choices=[(USER, "User"), (SYSTEM, "System")])
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name="+"
    )
    actor_membership = models.ForeignKey(
        "accounts.TenantMembership", null=True, on_delete=models.PROTECT, related_name="+"
    )
    action = models.TextField()
    resource_type = models.TextField()
    resource_id = models.UUIDField(null=True)
    outcome = models.TextField(choices=[(SUCCESS, "Success"), (DENIED, "Denied"), (ERROR, "Error")])
    occurred_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "audit_event"
        constraints = [
            models.CheckConstraint(
                condition=(Q(actor_type="user") & Q(actor_user__isnull=False))
                | (Q(actor_type="system") & Q(actor_user__isnull=True)),
                name="ck_ae_actor_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "occurred_at"], name="ix_ae_tenant_time"),
            models.Index(fields=["resource_type", "resource_id"], name="ix_ae_resource"),
        ]
