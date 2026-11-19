import unicodedata
import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Func, IntegerField, Q
from django.db.models.lookups import GreaterThanOrEqual

from apps.core.models import TenantScopedModel

# Tenant roles (features.md 6.1).
OWNER_ADMIN = "owner_admin"
CLINICAL_SUPERVISOR = "clinical_supervisor"
THERAPIST = "therapist"
ASSISTANT = "assistant"
ROLE_CHOICES = [
    (OWNER_ADMIN, "Owner / Admin"),
    (CLINICAL_SUPERVISOR, "Clinical supervisor"),
    (THERAPIST, "Therapist"),
    (ASSISTANT, "Assistant / Receptionist"),
]
ROLES = [code for code, _ in ROLE_CHOICES]

# Optional grants on top of roles (features.md 6.2 "if granted").
RECEPTIONIST_OPERATIONAL_ACCESS = "receptionist_operational_access"
SECURITY_METADATA_REVIEW = "security_metadata_review"
GRANT_CHOICES = [
    (RECEPTIONIST_OPERATIONAL_ACCESS, "Receptionist operational access"),
    (SECURITY_METADATA_REVIEW, "Security metadata review"),
]


def normalize_email(email):
    return unicodedata.normalize("NFKC", email or "").strip().lower()


class Tenant(models.Model):
    ACTIVE, SUSPENDED, CLOSED = "active", "suspended", "closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    slug = models.TextField(unique=True)
    timezone = models.TextField(default="Asia/Tehran")
    status = models.TextField(
        choices=[(ACTIVE, "Active"), (SUSPENDED, "Suspended"), (CLOSED, "Closed")], default=ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenant"
        constraints = [
            models.CheckConstraint(
                condition=~Q(status="closed") | Q(archived_at__isnull=False), name="ck_tenant_archived"
            ),
        ]

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, full_name=""):
        user = self.model(email=email, full_name=full_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(email_norm=normalize_email(username))


class User(AbstractBaseUser):
    """Global login identity (table app_user). Not tenant-owned."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.TextField()
    email_norm = models.TextField(unique=True, editable=False)
    password = models.CharField(max_length=128, db_column="password_hash")
    full_name = models.TextField()
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email_norm"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "full_name"]

    class Meta:
        db_table = "app_user"
        constraints = [
            models.CheckConstraint(
                condition=Q(is_active=True) | Q(deactivated_at__isnull=False),
                name="ck_user_active_consistent",
            ),
        ]

    def save(self, *args, **kwargs):
        self.email_norm = normalize_email(self.email)
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "email" in update_fields:
            kwargs["update_fields"] = {*update_fields, "email_norm"}
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class TenantMembership(TenantScopedModel):
    """A user's participation in one tenant, with roles."""

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="memberships")
    roles = ArrayField(models.TextField(choices=ROLE_CHOICES))
    joined_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenant_membership"
        constraints = [
            *TenantScopedModel.Meta.constraints,
            models.CheckConstraint(condition=Q(roles__contained_by=ROLES), name="ck_tm_roles_known"),
            models.CheckConstraint(
                condition=GreaterThanOrEqual(
                    Func(F("roles"), function="cardinality", output_field=IntegerField()), 1
                ),
                name="ck_tm_roles_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("joined_at")), name="ck_tm_dates"
            ),
            models.UniqueConstraint(
                fields=["tenant", "user"], condition=Q(ended_at__isnull=True), name="uq_tm_active_user"
            ),
        ]

    @property
    def is_active(self):
        return self.ended_at is None

    def has_role(self, role):
        return role in self.roles

    def has_grant(self, code):
        return self.grants.filter(grant_code=code, revoked_at__isnull=True).exists()


class MembershipGrant(TenantScopedModel):
    """Narrow optional permission on top of a membership's roles."""

    membership = models.ForeignKey(TenantMembership, on_delete=models.PROTECT, related_name="grants")
    grant_code = models.TextField(choices=GRANT_CHOICES)
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "membership_grant"
        constraints = [
            *TenantScopedModel.Meta.constraints,
            models.UniqueConstraint(
                fields=["tenant", "membership", "grant_code"],
                condition=Q(revoked_at__isnull=True),
                name="uq_mg_active",
            ),
        ]
