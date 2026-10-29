[← Back to index](../../README.md)

# MembershipGrant

> `membership_grant` · Group A: tenancy, identity, authentication

**Purpose:** extra, narrowly-scoped permissions that sit on top of a role. Implements the "if granted" and "explicit permission" wording of features.md 6.2 (X-3).

```sql
CREATE TABLE membership_grant (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL,
    membership_id UUID NOT NULL,
    grant_code    TEXT NOT NULL
                  CHECK (grant_code IN (
                      'receptionist_operational_access',
                      'security_metadata_review'
                  )),
    granted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at    TIMESTAMPTZ,
    CONSTRAINT fk_mg_membership
        FOREIGN KEY (membership_id, tenant_id)
        REFERENCES tenant_membership (id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_mg_id_tenant UNIQUE (id, tenant_id)
);
CREATE UNIQUE INDEX uq_mg_active
    ON membership_grant (tenant_id, membership_id, grant_code)
    WHERE revoked_at IS NULL;
```

**Grant codes**

| Code | Meaning |
|---|---|
| `receptionist_operational_access` | Lets a member do front-desk operational work (scheduling, demographics) without clinical access. |
| `security_metadata_review` | Lets a member review security/audit metadata. |

**Constraints explained**

- `fk_mg_membership`: composite FK, so a grant can only attach to a membership of the **same tenant**.
- `uq_mg_active` (partial unique): the same grant cannot be active twice for the same member. After revocation, it can be granted again as a new row, which preserves history.

**Design notes:** `grant_code` is intentionally a short, closed list. Adding a new code requires a schema change (altering the CHECK), not just a data change, so each new kind of power is a deliberate, reviewable event.

## Relationships

**Depends on (this table references):** [TenantMembership](tenant-membership.md)

**Referenced by:** no table

## Triggers on this table

None.

## See also

- [composite foreign key pattern](../../01-foundations/conventions.md) (how tenant isolation works)
- [declarative constraints](../../03-enforcement/declarative-constraints.md), [trigger summary](../../03-enforcement/triggers/README.md), [application-level rules](../../03-enforcement/application-level-rules.md), [documented limitations](../../03-enforcement/documented-limitations.md)
- [ER diagram](../../01-foundations/er-diagram.md)

---

[← TenantMembership](tenant-membership.md) · [Group overview](README.md) · [Session →](session.md)
