import uuid

from django.db import models


class TenantScopedModel(models.Model):
    """Base class for every tenant-owned table.

    The UNIQUE (id, tenant_id) key is what child tables target with composite
    foreign keys, so the database rejects cross-tenant links on write.
    Read isolation is enforced by apps.accounts.tenancy.TenantScopedViewSet.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("accounts.Tenant", on_delete=models.PROTECT, related_name="+")

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=["id", "tenant"], name="%(class)s_id_tenant_uq"),
        ]
