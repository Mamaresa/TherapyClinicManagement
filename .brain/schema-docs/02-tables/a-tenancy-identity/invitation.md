[← Back to index](../../README.md)

# Invitation

> `invitation` · Group A: tenancy, identity, authentication

**Purpose:** a pending offer for someone to join a tenant with a set of roles. Implements X-7.

```sql
CREATE TABLE invitation (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
    invited_email           TEXT NOT NULL,
    invited_email_norm      TEXT NOT NULL,
    role_set                TEXT[] NOT NULL
                            CHECK (role_set <@ ARRAY['owner_admin','clinical_supervisor','therapist','assistant']::TEXT[]),
    invited_by_membership_id UUID NOT NULL,
    issued_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at              TIMESTAMPTZ NOT NULL,
    accepted_at             TIMESTAMPTZ,
    revoked_at              TIMESTAMPTZ,
    CONSTRAINT fk_inv_inviter
        FOREIGN KEY (invited_by_membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT ck_inv_dates CHECK (expires_at > issued_at),
    CONSTRAINT ck_inv_state CHECK (
        NOT (accepted_at IS NOT NULL AND revoked_at IS NOT NULL)
    )
);
CREATE INDEX ix_inv_tenant_open
    ON invitation (tenant_id, invited_email_norm)
    WHERE accepted_at IS NULL AND revoked_at IS NULL;
```

**Constraints explained**

- `fk_inv_inviter`: the inviter must be a member of the same tenant.
- `ck_inv_state`: an invitation cannot be both accepted and revoked.
- `ix_inv_tenant_open`: finds still-open invitations for an email within a tenant.

**Design notes**

- **No email enumeration.** Responses to invitation attempts must not reveal whether `invited_email_norm` already exists in `app_user`. The schema cannot enforce this because the query itself is what would leak. It is an **application** rule.
- Accepting an invitation creates a `tenant_membership` and sets `accepted_at`. Those two writes should happen in one transaction.
- Unlike `role_set`'s CHECK, there is no minimum-length rule here, so an invitation with an empty role set is not rejected by the schema (see [review notes on Part 1](../../05-notes/review-notes-part1.md)).

## Relationships

**Depends on (this table references):** [Tenant](tenant.md), [TenantMembership](tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← ResetToken](reset-token.md) · [Group overview](README.md) · [PlatformRole →](platform-role.md)
